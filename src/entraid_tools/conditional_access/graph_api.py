from ..helpers.graph_api import APIResponse, EntityAPI


class PoliciesAPI(EntityAPI):
    def _get_entity_path(self) -> str:
        return "identity/conditionalAccess/policies"

    def rename(self, policy_id: str, new_name: str) -> APIResponse:
        """Renames a conditional access policy"""
        payload = {"displayName": new_name}
        return self.update(policy_id, payload)
