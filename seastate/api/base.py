from abc import ABC, abstractmethod
from seastate.settings import DATASOURCES
from seastate.exceptions import SeaStateException
from datetime import datetime
from typing import Dict, Optional, Union
from seastate.models import Result


class BaseApi(ABC):
    def __init__():
        raise NotImplementedError

    @property
    def id(self) -> str:
        """filename of the API module used internally as the id"""
        id = self.__module__.split(".")[-1]
        # integration check
        if id not in DATASOURCES:
            raise SeaStateException(f"API filename {id} does not match DATASOURCES")
        return id

    def measurement_from_date_range(
        self, measurement: str, station_id: str, start: datetime, end: datetime
    ) -> list[Dict]:
        # build endpoint
        ep, ep_params = self._build_endpoint(measurement, station_id, start, end)
        # get result
        result = self._get_result(ep, ep_params)
        # parse result to data
        data = self._parse_result(result, start, end, measurement)
        return data

    @abstractmethod
    def _build_endpoint(
        self, measurement: str, station_id: str, start: datetime, end: datetime
    ) -> (str, Dict):
        pass

    @abstractmethod
    def _build_parse_key(self, measurement: str = None) -> Union[str, list[str], None]:
        pass

    def _get_result(
        self, endpoints: list[str], ep_params: Optional[Dict] = None
    ) -> list[Result]:
        """ep_params is applied to each endpoint in endpoints"""
        if isinstance(endpoints, str):
            endpoints = [endpoints]
        return [self._adapter.get(endpoint=ep, ep_params=ep_params) for ep in endpoints]

    @abstractmethod
    def _parse_result(
        self, result: list[Result], start: datetime, end: datetime, measurement: str
    ) -> Dict:
        pass
