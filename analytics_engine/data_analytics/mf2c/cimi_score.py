# Copyright (c) 2017, Intel Research and Development Ireland Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Giuliana Carullo'
__copyright__ = "Copyright (c) 2019, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"

import pandas
import analytics_engine.common as common
from analytics_engine.infrastructure_manager.cimiclient import cimi

# from lib_analytics

LOG = common.LOG


class CimiScore(object):

    @staticmethod
    def utilization_scores(devices):
        """
        Returns a dictionary with the scores of
        all the nodes of the graph.

        :param graph: InfoGraph
        :return: dict[node_name] = score
        """
        res = dict()
        for device in devices:
            dev_id = device.get("id").split("/")[1]
            dynamics = cimi.get_device_dynamics_by_device_id(dev_id)
            
            if dynamics:
                res[dev_id] = dict()
                res[dev_id]['memory']= round(float(dynamics.get("cpuFreePercent", 0)),1)
                res[dev_id]['compute'] = round(float(dynamics.get("cpuFreePercent", 0)),1)
                res[dev_id]['disk'] = round(float(dynamics.get("storageFreePercent", 0)),1)
                res[dev_id]['network'] = 0

        return res

    @staticmethod
    def saturation_scores(devices):
        """
        Returns a dictionary with the scores of
        all the nodes of the graph.

        :param graph: InfoGraph
        :return: dict[node_name] = score
        """
        res = dict()
        for device in devices:
            node_name = device.get("id").split("/")[1]
            res[node_name] = dict()
            LOG = common.LOG

            res[node_name]['compute'] = 0
            res[node_name]['disk'] = 0
            res[node_name]['network'] = 0
            res[node_name]['memory'] = 0
        return res

    @staticmethod
    def _calc_score(utilization=1, saturation=0, capacity=1):
        """
        Returns the score related to the utilization
        """
        if utilization > 1 or utilization < 0:
            raise ValueError("Utilization must be in the range 0-1")
        if saturation > 1 or saturation < 0:
            raise ValueError("Saturation must be in the range 0-1")
        if capacity > 1 or capacity < 0:
            raise ValueError("Capacity must be in the range 0-1")

        score = (1 - saturation) * float(capacity) / (1 + float(utilization))
        return score



