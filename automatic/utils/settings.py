import os, re, shutil
from string import Template
import conf


class SETTINGS():
    module = None
    server_id = 0
    host_id = 0

    def __init__(self, module, server_id=0, host_id=0):
        self.module = module
        self.server_id = server_id
        self.host_id = host_id

    def get_combined_file(self, common=None, host=None, combined=None):
        if common is None or host is None or combined is None:
            return False
        if not os.path.isfile(common):
            return
        if not os.path.isfile(host):
            shutil.copy(common, combined)
        f = open(common, 'r')
        lines_common = f.readlines()
        f.close()
        f = open(host, 'r')
        lines_host = f.readlines()
        f.close()
        lines_combined = self.combine_settings(lines_common, lines_host)
        f = open(combined, 'w')
        f.writelines(lines_combined)
        f.close()
        if os.path.isfile(combined):
            return True
        else:
            return False


    def get_host_settings(self, server_id=0, host_id=0, ):
        if server_id != 0:
            self.server_id = server_id
        if host_id != 0:
            self.host_id = host_id
        host_file = conf.settings_file_location + self.module + '/' + conf.settings_file_name[
            self.module] + '@' + server_id + '_' + host_id
        common_file = conf.settings_file_location + self.module + '/' + conf.settings_file_name[self.module] + '@0_0'
        return (common_file, host_file)

    def map_host_info(self, server, settings):
        if server is not None and settings is not None:
            server_name = server.server_name
            host = server.server_host[self.host_id]
            host_path = server.server_path[self.host_id][self.module]
            db_info = server.server_db[self.module]
            s_template = Template(settings)
            s_template = s_template.safe_substitute(server_name=server_name, host=host['host'],
                                                    path=host_path['des_path'])
            s_template = s_template.safe_substitute(db_host=db_info['host'], db_port=db_info['port'],
                                                    db_name=db_info['name'], db_user=db_info['user'],
                                                    db_pass=db_info['pass'])
            return str(s_template)
        else:
            return None

    def get_index(self, lines):
        block_index = []
        block_dict = {}
        marker = re.compile('^#↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓\.[0-9]+\.↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓\n*$')
        for line in lines:
            match = marker.search(line)
            if match:
                index = line[line.find('↓.') + 2:line.find('.↓')]
                line_num = lines.index(line)
                if index not in block_index:
                    block_index.append(index)
                    block_dict[index] = [line_num]
        marker = re.compile('^#↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑\.[0-9]+\.↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑\n*$')
        for line in lines:
            match = marker.search(line)
            if match:
                index = line[line.find('↑.') + 2:line.find('.↑')]
                line_num = lines.index(line)
                if index in block_index:
                    if line_num > block_dict[index][0]:
                        block_dict[index].append(line_num)
                    else:
                        del block_dict[index]
                        block_index.remove(index)
        for index in block_index:
            if len(block_dict[index]) < 2:
                del block_dict[index]
                block_index.remove(index)
        return (block_index, block_dict)

    def rm_dismatch_index(self, c_index, h_index):
        for index in c_index:
            if index not in h_index:
                c_index.remove(index)
        return c_index

    def combine_settings(self, common_lines, host_lines):
        combined = []
        line_counter = 0
        c_block_index, c_block_dict = self.get_index(common_lines)
        h_block_index, h_block_dict = self.get_index(host_lines)
        c_block_index = self.rm_dismatch_index(c_block_index, h_block_index)
        for index in c_block_index:
            c_line_start = c_block_dict[index][0]
            c_line_end = c_block_dict[index][1] + 1
            h_line_start = h_block_dict[index][0] + 1
            h_line_end = h_block_dict[index][1]
            for line in common_lines[line_counter:c_line_start]:
                combined.append(line)
            if h_line_start == h_line_end:
                combined.append(host_lines[h_line_start])
            else:
                for line in host_lines[h_line_start:h_line_end]:
                    if line != 'None':
                        combined.append(line)
            line_counter = c_line_end
        for line in common_lines[line_counter:]:
            combined.append(line)
        return combined
