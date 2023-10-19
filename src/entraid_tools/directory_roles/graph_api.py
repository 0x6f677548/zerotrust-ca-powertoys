from ..helpers.graph_api import APIResponse, EntityAPI


class DirectoryRolesAPI(EntityAPI):
    def _get_entity_path(self) -> str:
        return "directoryRoles"


class DirectoryRoleTemplatesAPI(EntityAPI):
    def _get_entity_path(self) -> str:
        return "directoryRoleTemplates"

    def get_by_display_name(self, display_name: str) -> APIResponse:
        """Returns a directory role template by its display name"""

        assert display_name, "display_name cannot be None"

        # this entity does not support filters neither page size, so we'll have to
        # get all the entities and filter them ourselves

        response = self.get_all()

        if response.success:
            # move the value property to the response property
            response.response = response.json()["value"]
            for entity in response.response:
                if entity["displayName"] == display_name:
                    response.response = entity
                    return response

            response.success = False
            response.status_code = 404
            response.response = "No results found"

        return response
