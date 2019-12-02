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

__author__ = 'Marcin Spoczynski'
__copyright__ = "Copyright (c) 2019, Intel"
__license__ = "Apache 2.0"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"

from analytics_engine import common
from analytics_engine.data_analytics.mf2c.cimi_score import CimiScore
from analytics_engine.infrastructure_manager.cimiclient import cimi
import pandas as pd
from analytics_engine.heuristics.filters.base import Filter

LOG = common.LOG


class OptimalFilter(Filter):

    __filter_name__ = 'optimal_filter_cimi'

    def run(self, workload, optimal_node_type='x86_64'):
        """
        Ranks machines by CPU utilization.

        :param workload: Contains workload related info and results.

        :return: heuristic results
        """
        workload_config = workload.get_configuration()

        devices = cimi.get_devices()

        scores = CimiScore.utilization_scores(devices)
        scores_sat = CimiScore.saturation_scores(devices)
        heuristic_results = pd.DataFrame(columns=['node_name', 'type', 'ipaddress', 
                                                  'compute utilization', 'compute saturation',
                                                  'memory utilization', 'memory saturation',
                                                  'network utilization', 'network saturation',
                                                  'disk utilization', 'disk saturation',
                                                  ])
        heuristic_results_nt = heuristic_results.copy()
        device_id_col_name = None
        if workload_config.get('project'):
            project = workload_config.get('project')
            device_id_col_name = project+'_device_id'
            heuristic_results[device_id_col_name] = None
        else:
            device_id_col_name = 'mf2c_device_id'
            heuristic_results[device_id_col_name] = None

        workload_name = workload_config.get('name')
        #workload_name = workload_name[8:]

        service_config = cimi.get_services_by_name(workload_name)
        LOG.info(service_config)

        if len(service_config) > 0:
            sensors_req = service_config[0].get("req_resource")
            agent_type = service_config[0].get("agent_type")
        sensorsPass = True 
        agentPass = True
        for node in cimi.get_devices():
            node_name = node.get("id").split("/")[1]
            dd = cimi.get_device_dynamics_by_device_id(node_name)
            if agent_type:
                if agent_type != node.get("agent_type"):
                    agentPass = False
            
            if sensors_req:
                sensors = dd.get("sensors", [{}])
                sensors_type = sensors[0].get('sensorType')
                if sensors_type != "None":
                    if sorted(sensors_type) != sorted(sensors_req):
                        sensorsPass = False

            ip_address = dd.get("wifiAddress", "")

            node_type = node.get("arch")
            list_node_name = node_name
            if node_type == optimal_node_type and sensorsPass and agentPass:
                data = {'node_name': list_node_name,
                                                    'type': node_type,
                                                    'ipaddress': ip_address,
                                                    'compute utilization': scores[node_name]['compute'],
                                                    'compute saturation': scores_sat[node_name]['compute'],
                                                    'memory utilization': scores[node_name]['memory'],
                                                    'memory saturation': scores_sat[node_name]['memory'],
                                                    'network utilization': scores[node_name]['network'],
                                                    'network saturation': scores_sat[node_name]['network'],
                                                    'disk utilization': scores[node_name]['disk'],
                                                    'disk saturation': scores_sat[node_name]['disk']}
                
                data[device_id_col_name] = node_name
                
                heuristic_results = heuristic_results.append(data, ignore_index=True)

        sort_fields = ['compute utilization']
        sort_order = workload_config.get('sort_order')
        if sort_order:
            sort_fields = []
            for val in sort_order:
                if val == 'cpu':
                    sort_fields.append('compute utilization')
                if val == 'memory':
                    sort_fields.append('memory utilization')
                if val == 'network':
                    sort_fields.append('network utilization')
                if val == 'disk':
                    sort_fields.append('disk utilization')
        heuristic_results_nt = heuristic_results_nt.replace([0], [None])
        heuristic_results = heuristic_results.sort_values(by=sort_fields, ascending=True)
        heuristic_results = heuristic_results.append(heuristic_results_nt, ignore_index=True)
        workload.append_metadata(self.__filter_name__, heuristic_results)
        LOG.info('AVG: {}'.format(heuristic_results))
        return heuristic_results




