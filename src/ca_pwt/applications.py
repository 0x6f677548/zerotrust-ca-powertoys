import logging
from ca_pwt.helpers.graph_api import EntityAPI, APIResponse
from ca_pwt.helpers.utils import assert_condition

_logger = logging.getLogger(__name__)

_BUILTIN_APPS_TO_IGNORE = {"All": "All", "None": "None", "Office365": "Office365"}


class ServicePrincipalsAPI(EntityAPI):
    def _get_entity_path(self) -> str:
        return "servicePrincipals"

    def get_by_app_id(self, app_id: str) -> APIResponse:
        """Gets service principal found with the given app_id
        Returns an API_Response object and the entity is in the json property of the API_Response object
        """
        assert_condition(app_id, "app_id cannot be None")
        url = f"{self.entity_url}(appId='" + "{" + app_id + "}')"
        self._logger.info(url)
        return self._request_get(url=url)
