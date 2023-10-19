from .helpers.graph_api import APIResponse, EntityAPI


class UsersAPI(EntityAPI):
    def _get_entity_path(self) -> str:
        return "users"

    def get_by_id(self, entity_id: str) -> APIResponse:
        """Returns a user by their ID which can be the id attribute
        or the userPrincipalName attribute
        """

        assert entity_id, "entity_id cannot be None"

        # encode the hash symbol in the entity_id
        entity_id = entity_id.replace("#", "%23")

        if entity_id.startswith("$"):
            url = f"{self.entity_url}({entity_id})"
        else:
            url = f"{self.entity_url}/{entity_id}"
        return self._request_get(url)
