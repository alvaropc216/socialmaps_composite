import copy
from flask import request
import json
import logging
from datetime import datetime

logger = logging.getLogger()

"""
RestContext allows to source the arguments used in the call
"""


class RESTContext:
    _default_limit = 10

    def __init__(self, request_context, path_parameters=None):
        log_message = ""
        self.limit = RESTContext._default_limit
        self.max_limit = 10

        self.path = request_context.path
        args = dict(request_context.args)
        args = self._de_array_args(args)
        self.path = request.path

        self.data = None
        self.headers = dict(request.headers)
        self.method = request.method
        self.host_url = request.host_url
        self.full_path = request.full_path
        self.base_url = request.base_url
        self.url = request.url

        self.path_parameters = path_parameters

        try:
            self.data = request_context.get_json()
        except Exception as e:
            pass

        args, limit = self._get_and_remove_args(args, 'limit')
        if limit is not None:
            self.limit = limit

        if int(self.limit) > self.max_limit:
            self.limit = str(self.max_limit)

        args, offset = self._get_and_remove_args(args, "offset")
        self.offset = offset

        args, order_by = self._get_and_remove_args(args, "order_by")
        self.order_by = order_by

        args, fields = self._get_and_remove_args(args, "fields")
        if fields is not None:
            fields = fields.split(",")
        self.fields = fields
        self.args = args

        try:
            if request.data is not None:
                data = request.json
            else:
                data = None
        except Exception as e:
            data = "Data was not in JSON Format"
            log_message = str(datetime.now())+": Method " +self.method
        log_message+=" received: \n"+json.dumps(str(self), indent=2)
        logger.debug(log_message)


    @staticmethod
    def _de_array_args(args):
        result = {}
        if args is not None:
            for k,v in args.items():
                if type(v) == list:
                    result[k] = ",".join(v)
                else:
                    result[k] = v
        return result

    @staticmethod
    def _get_and_remove_args(args,arg_name):
        val = copy.copy(args.get(arg_name,None))
        if val is not None:
            del args[arg_name]
        return args, val

    def add_pagination(self, response_size, response_data):
        page_info = []
        self_link = {
            "rel": "self",
            "href": self.url,
            "type:": "GET"
        }
        page_info.append(self_link)

        if self.limit is not None:
            current_limit = int(self.limit)
            if self.offset is not None:
                current_offset = int(self.offset)
            else:
                current_offset = 0
            data_len = response_size
            base_url = self.construct_base_url_without_limit_offset()

            # Do we need to add a next link?
            if data_len - current_offset >= current_limit:
                next_offset = current_offset + current_limit
                next_link = base_url + "&offset=" + str(next_offset) + "&limit=" + str(current_limit)

                page_info.append(
                    {
                        "rel": "next",
                        "href": next_link,
                        "type": "GET"
                    }
                )

            # Do we need a previous link?
            if current_offset>0:
                previous_offset = max(current_offset-current_limit,0)
                previous_link = base_url + "&offset=" + str(previous_offset) + "&limit=" + str(current_limit)

                page_info.append(
                    {
                        "rel": "prev",
                        "href": previous_link,
                        "type": "GET"
                    }
                )

        result = {
            "data": response_data,
            "links": page_info
        }

        return result

    def construct_base_url_without_limit_offset(self):
        result = self.base_url
        if self.args:
            qs=[]
            for k,v in self.args.items():
                qs.append(k + "=" + v)
            qs = "?" + "&".join(qs)
            result += qs
        else:
            result += "?"
        return result

