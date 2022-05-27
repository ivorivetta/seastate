import requests
import requests.packages
from typing import List, Dict

from ocean_sdk.exceptions import OceanSDKException
from ocean_sdk.models import Result

from json import JSONDecodeError

class RestAdapter:
    def __init__(self, hostname: str, api_key: str = '', ver: str = 'v1', ssl_verify: bool = True):
        self.url = "https://{}/{}/".format(hostname, ver)
        self._api_key = api_key
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings()
            
    def _do(self, http_method, endpoint:str, ep_params: Dict = None, data: Dict = None ) -> Result:
        full_url = self.url + endpoint
        headers = {'x-api-key': self._api_key}
        try:
            response = requests.request(
                method=http_method,
                url=full_url,
                verify=self._ssl_verify,
                headers=headers,
                params=ep_params,
                json=data)
        except requests.exceptions.requests.RequestException as e:
            raise OceanSDKException("NOAA Request Failed") from e
        try:
            data_out = response.json()
        except (ValueError, JSONDecodeError) as e:
            raise OceanSDKException()
        if 299 >= response.status_code >= 200:
            return Result(response.status_code, message=response.reason, data=data_out)
        raise OceanSDKException(f"{response.status_code}: {response.reason}")
            
    def get(self, endpoint: str, ep_params: Dict = None) -> Result:
        return self._do(http_method='GET', endpoint=endpoint, ep_params=ep_params)