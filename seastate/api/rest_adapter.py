import logging
from typing import Dict, Union

import requests
import requests.packages
from requests_cache import CachedSession
from seastate.exceptions import SeaStateException
from seastate.models import Result


class RestAdapter:
    session = CachedSession("seastate_cache", backend="filesystem", use_cache_dir=True)

    def __init__(
        self,
        hostname: str,
        api_key: str = None,
        ssl_verify: bool = True,
        logger: logging.Logger = None,
    ):
        """Constructor for RestAdapter, supports GET

        Args:
            hostname (str): hostname for http request
            api_key (str, optional): Defaults to ''.
            ssl_verify (bool, optional): Defaults to True.
        """
        self._logger = logger or logging.getLogger(__name__)
        self.url = f"https://{hostname}/"
        self._api_key = api_key
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings()

    def _do(
        self, http_method: str, endpoint: str, ep_params: Dict = None, data: Dict = None
    ) -> Result:
        """HTTP request contructor convenience method

        Args:
            http_method (_type_): GET, POST, DELETE
            endpoint (str): target endpoint
            ep_params (Dict, optional): http parameters. Defaults to None.
            data (Dict, optional): POST data. Defaults to None.

        Returns:
            Result: Simplified http.Response object with:
                status_code
                message
                data
        """
        full_url = self.url + endpoint
        headers = {"x-api-key": self._api_key}
        log_line_pre = f"method={http_method}, url={full_url}, params={ep_params}"
        log_line_post = "result: success={}, status_code={}, message={}"
        # Log HTTP params and try HTTP request
        try:
            self._logger.debug(msg=log_line_pre)
            # response = requests.request(
            response = self.session.request(
                method=http_method,
                url=full_url,
                verify=self._ssl_verify,
                headers=headers,
                params=ep_params,
                json=data,
            )
        except Exception as e:
            self._logger.exception(msg=str(e))
            raise SeaStateException("Request Failed") from e
        # Parse JSON ouput to Python object or return failed Result on exception
        try:
            if ".txt" in full_url.lower():
                # handle txt based files from nonRest endpoints
                data_out = response.text
            elif "xml" in full_url.lower():
                # handle xml files from nonRest endpoints
                data_out = response.text
            elif any(x in full_url.lower() for x in ["spec", ".sw"]):
                # handle the 7 different spectral file extensions
                data_out = response.text
            else:
                # handle a restful endpoint
                data_out = response.json()
        except ValueError as e:
            self._logger.error(msg=log_line_post.format(False, None, e))
            raise SeaStateException("Bad JSON in Response") from e
        is_success = 299 >= response.status_code >= 200
        log_line = log_line_post.format(
            is_success, response.status_code, response.reason
        )
        # if status code in 200-299 range, return Result, else raise exception
        if is_success:
            self._logger.debug(msg=log_line)
            return Result(response.status_code, message=response.reason, data=data_out)
        self._logger.error(msg=log_line)
        raise SeaStateException(f"{response.status_code}: {response.reason}")

    def get(self, endpoint: str, ep_params: Union[Dict, None] = None) -> Result:
        """GET method for RestAdapter

        Args:
            endpoint (str): target endpoint
            ep_params (Dict, optional): key:value API parameters. Defaults to None.

        Returns:
            Result: Simplified Response object with:
                status_code
                message
                data
        """
        return self._do(http_method="GET", endpoint=endpoint, ep_params=ep_params)
