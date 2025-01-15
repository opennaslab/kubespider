from urllib.parse import urlparse, parse_qs

class MagnetUrl(object):
    url = None
    xturn_delimiter = ':'

    def __init__(self, url):
        self.url = url

    @property
    def files(self):
        files = []
        index = 0
        has_data = lambda e: any([x is not None for x in list(e.values())])
        entry = self.__file_entry(0)
        while has_data(entry):
            files.append(entry)
            index += 1
            entry = self.__file_entry(index)
        return files

    @property
    def trackers(self):
        return self.data.get('tr', [])

    @property
    def acceptable_sources(self):
        return self.data.get('xs', [])

    @property
    def data(self):
        if hasattr(self, '_data'):
            return getattr(self, '_data')
        self._data = self.__parse(self.url)
        return self._data

    def __parse(self, url):
        parsed = urlparse(url)
        if parsed.scheme != 'magnet':
            return {}
        data = parse_qs(parsed.query or parsed.path[1:])
        query_data = {}
        for param_name, values_list in list(data.items()):
            if len(values_list) == 1:
                query_data[param_name] = values_list[0]
            else:
                query_data[param_name] = values_list
        return query_data

    def __display_name(self, index=None):
        return self.data_index('dn', index)

    def data_index(self, fieldname, index=None):
        data_fieldname = "%s.%s" % (fieldname, index) if index else fieldname
        return self.data.get(data_fieldname)

    def __hash_type(self, index=None):
        xturn = self.data_index('xt', index)
        if not xturn:
            return
        return ' '.join(xturn.split(self.xturn_delimiter)[1:-1])

    def __hash(self, index=None):
        xturn = self.data_index('xt', index)
        if not xturn:
            return
        return xturn.split(self.xturn_delimiter)[-1]

    def __data_size(self, index=None):
        return self.data_index('xl', index)

    def __file_entry(self, index):
        return dict(
            display_name=self.__display_name(index),
            data_size=self.__data_size(index),
            hash_type=self.__hash_type(index),
            hash=self.__hash(index))

    def Resolve(self):
        char = ".torrent"
        if self.files[0]['display_name'] is not None:
            result = self.files[0]['display_name']
        else:
            for key in self.data.keys():
                if "dn" in key:
                    result = self.data[key]
                    break
                else:
                    result = "No Name Found"
        if result.endswith(char):
            result = result[:-len(char)]

        return result