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

__author__ = 'Sridhar Voorakkara'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"

import analytics_engine.infrastructure_manager.cimiclient.cimi as cimiclient
from analytics_engine.heuristics.filters.base import Filter
import analytics_engine.common as common

LOG = common.LOG

class CimiFilter(Filter):

    def __init__(self):
        pass

    def run(self, recipe):
        recipe_json = recipe.to_json()
        service_id = None
        if recipe_json.get("service_id"):
            service_id = recipe_json['service_id']
            if not recipe_json.get('name'):
                service = cimiclient.get_service(service_id)
                if service:
                    recipe.name = service.get('name')
                else:
                    recipe.name = service_id
        elif recipe_json.get('name'):
            # get service from CIMI for finding the service id
            services = cimiclient.get_services_by_name(recipe_json['name'])
            err = ""
            if len(services) > 1:
                LOG.info("More than one CIMI services found with the provided name. No CIMI update will be done!")
            elif len(services) == 0:
                LOG.info("No CIMI services found with the provided name. No CIMI update will be done!")
            else:
                service = services[0]
                recipe.service_id = service['id']
        return recipe

    def refine(self, recipe):
        recipe_json = recipe.to_json()
        if recipe_json.get("service_id"):
            service_id = recipe_json['service_id']
        if service_id:
            category = recipe_json.get("category")
            service_update = dict()
            service_update['memory'] = category['memory']
            cimiclient.update_service(service_id, service_update)
            LOG.info("Refinement updated to CIMI")
