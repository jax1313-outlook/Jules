#!/usr/bin/env python3
"""
Cross-repo integration walkthrough for the Tri-Department Matrix Build.

This is a build-verification script, NOT application code (per
07_DISPATCH_REPO_PLACEMENT_PLAN.md, Claude-3 does not contain production application code — this
script exists to produce evidence for the Cross-Repo Relationship Report and does not run as part
of any department's own runtime). It imports the three department repos' packages directly from
their checkout paths (passed as CLI args or environment variables) and drives one real object
through the full Intelligence -> Library -> Publisher chain, proving the shared contracts in
DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md are not just parallel documentation but are actually
field-compatible across repos with no shared package dependency.

Usage:
    python3 cross_repo_walkthrough.py <intel_src> <library_src> <publisher_src>

Exits non-zero and prints a Conflict Notice-style message if any integration assertion fails.
"""
import dataclasses
import sys


def main(intel_src: str, library_src: str, publisher_src: str) -> None:
    sys.path.insert(0, intel_src)
    sys.path.insert(0, library_src)
    sys.path.insert(0, publisher_src)

    from dispatch_intel import service as intel_service
    from dispatch_intel.store import IntelligenceStore

    from dispatch_library.service import LibraryService
    from dispatch_library.models import LibraryCandidate as LibLibraryCandidate
    from dispatch_library.models import SubmittedBy as LibSubmittedBy
    from dispatch_library.models import RecipeType as LibRecipeType
    from dispatch_library.models import PublisherRecipe as LibPublisherRecipe

    from dispatch_publisher import service as pub_service
    from dispatch_publisher.library_client import LibraryClient
    from dispatch_publisher.models import RecipeType as PubRecipeType

    print("=== STEP 1: Intelligence — analyze a real example document ===")
    store = IntelligenceStore()
    finding = intel_service.create_finding(
        f"{intel_src}/../examples/load_board/sample_load.txt", store=store
    )
    print(f"Finding {finding.finding_id}: routing_queue={finding.routing_queue}")
    assert "LIBRARY_CANDIDATE" in finding.routing_queue, "expected sample load to nominate a Library candidate"

    from dispatch_intel.analyzer import analyze_document
    analysis = analyze_document(f"{intel_src}/../examples/load_board/sample_load.txt")
    intel_candidate = intel_service.route_to_library(
        finding,
        analysis_operational_signals=analysis["operational_signals"],
        analysis_government_signals=analysis["government_signals"],
        store=store,
    )
    assert intel_candidate is not None
    print(f"Intelligence LibraryCandidate: {intel_candidate.candidate_id} "
          f"collection={intel_candidate.collection} status={intel_candidate.status}")

    print("\n=== STEP 2: Field-compatibility check — Intelligence candidate -> Library candidate ===")
    intel_fields = {f.name for f in dataclasses.fields(intel_candidate)}
    lib_fields = {f.name for f in dataclasses.fields(LibLibraryCandidate)}
    assert intel_fields == lib_fields, (
        f"CONTRACT DRIFT: Intelligence LibraryCandidate fields {intel_fields} != "
        f"Library LibraryCandidate fields {lib_fields}"
    )
    print(f"Field sets identical across repos: {sorted(intel_fields)}")

    # Reconstruct the object on the Library side using the exact field values produced by
    # Intelligence, minus generated identity fields Library will assign itself. This is the
    # real integration point: no translation layer, no field renaming.
    payload = intel_candidate.to_dict()
    lib_candidate = LibLibraryCandidate(
        submitted_by=LibSubmittedBy(payload["submitted_by"]),
        source_type=payload["source_type"],
        collection=payload["collection"],
        proposed_object_code=payload["proposed_object_code"],
        proposed_title=payload["proposed_title"],
        proposed_body_or_reference=payload["proposed_body_or_reference"],
        source_finding_id=payload["source_finding_id"],
    )
    print("Reconstructed on Library side with zero field renaming.")

    print("\n=== STEP 3: Library — submit, review, and promote the candidate ===")
    library = LibraryService()
    library.submit_candidate(lib_candidate)
    assert library.current(lib_candidate.proposed_object_code) is None, "candidate must not be truth before review"

    reviewed = library.review_candidate(lib_candidate.candidate_id, approve=True, reviewed_by="Mike Zachary")
    assert reviewed.status.value == "APPROVED"
    promoted = library.current(lib_candidate.proposed_object_code)
    assert promoted is not None
    print(f"Candidate promoted to Library truth: {promoted.object_code} v{promoted.version} "
          f"source={promoted.source.value} accepted_by={promoted.accepted_by}")

    print("\n=== STEP 4: Library — ingest two human-placed Publisher Parts, register a recipe ===")
    library.ingest_human_document("W9-TEMPLATE", "Publisher_Parts", "W9 Template", "body", "Mike Zachary")
    library.ingest_human_document("COI-TEMPLATE", "Publisher_Parts", "COI Template", "body", "Mike Zachary")
    library.register_recipe(
        LibPublisherRecipe(
            recipe_code="RECIPE-BROKER-v1",
            recipe_type=LibRecipeType.BROKER_ONBOARDING_PACKET,
            version=1,
            required_library_object_codes=["W9-TEMPLATE", "COI-TEMPLATE", "MISSING-ITEM-X"],
        )
    )
    print("Registered BROKER_ONBOARDING_PACKET recipe requiring 2 present items + 1 deliberately missing item.")

    print("\n=== STEP 5: Publisher — pull from Library through the documented client boundary ===")

    class LiveLibraryAdapter:
        """Adapter proving Publisher's LibraryClient Protocol is satisfied by the real LibraryService."""

        def __init__(self, service: LibraryService) -> None:
            self._service = service

        def current(self, object_code: str):
            return self._service.current(object_code)

        def get_recipe(self, recipe_type: str):
            recipe = self._service.recipe_registry.get_current(LibRecipeType(recipe_type))
            if recipe is None:
                return None
            return recipe.to_dict()

        def resolve_packet(self, recipe_type: str):
            return self._service.resolve_packet(LibRecipeType(recipe_type))

    adapter: LibraryClient = LiveLibraryAdapter(library)
    request = pub_service.create_request("RECIPE-BROKER-v1", PubRecipeType.BROKER_ONBOARDING_PACKET)
    workspace = pub_service.pull_libraries(request, adapter)
    print(f"Workspace pulled={list(workspace.pulled_library_objects.keys())} "
          f"pending={workspace.pending_parts}")
    assert set(workspace.pulled_library_objects.keys()) == {"W9-TEMPLATE", "COI-TEMPLATE"}
    assert workspace.pending_parts == ["MISSING-ITEM-X"], "missing item must surface, not be fabricated"

    packet = pub_service.create_readiness_packet(request, workspace)
    inventory = pub_service.create_inventory(packet)
    notice = pub_service.create_missing_notice(inventory)
    review = pub_service.create_review_package(request, packet, inventory, notice)
    print(f"ReadinessPacket overall_status={packet.overall_status.value}, "
          f"ReviewPackage status={review.status.value}")
    assert packet.overall_status.value == "INCOMPLETE"
    assert notice is not None and notice.missing_items == ["MISSING-ITEM-X"]

    print("\n=== STEP 6: Publisher — self-approval blocked, external approval succeeds ===")
    try:
        pub_service.approve_review_package(review, "PUBLISHER")
        raise SystemExit("CONFLICT: Publisher was able to approve its own review package")
    except ValueError as e:
        print(f"Self-approval correctly blocked: {e}")

    pub_service.approve_review_package(review, "Mike Zachary")
    handoff = pub_service.create_archive_handoff(review)
    print(f"ArchiveHandoffPackage created: {handoff.handoff_id}, manifest={handoff.bundle_manifest}")

    print("\n=== ALL INTEGRATION ASSERTIONS PASSED ===")
    print("This is a recommendation only. No action is authorized. Mike decides.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    main(*sys.argv[1:4])
