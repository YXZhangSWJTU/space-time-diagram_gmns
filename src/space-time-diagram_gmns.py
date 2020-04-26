# coding=gb18030
# date 04/22/2020

import matplotlib.pyplot as plt

g_number_of_nodes = 0
g_number_of_road_links = 0
g_number_of_agents = 0
g_node_list = []
g_road_link_list = []
g_agent_list = []
g_internal_node_seq_no_dict = {}
g_external_node_id_dict = {}
g_internal_road_link_seq_no_dict = {}
g_external_road_link_id_dict = {}
g_link_key_to_seq_no_dict = {}
# default unit value of x axis is 1 min
g_x_axis_unit = 1  # in minutes

class Node:
    def __init__(self):
        self.name = ''
        self.node_id = 0
        self.node_seq_no = 0
        self.x_corrd = 0
        self.y_coord = 0
        self.display_coord = 0


class Link:
    def __init__(self):
        self.name = ''
        self.road_link_id = 0
        self.from_node_id = 0
        self.to_node_id = 0
        self.road_link_seq_no = 0
        self.from_node_seq_no = 0
        self.to_node_seq_no = 0
        self.length = 0
        self.display_sequence = 0
        self.left_corrd = 0
        self.right_corrd = 0


class Agent:
    def __init__(self):
        self.agent_id = 0
        self.o_node_id = 0
        self.d_node_id = 0
        self.o_node_seq_no = 0
        self.d_node_seq_no = 0
        self.node_sequence = []
        self.time_sequence = []  # in minutes
        self.xlist = []  # the time coordinate
        self.ylist = []  # the space coordinate
        self.agent_type = ''


def g_time_parser(time_sequence_list):
    output_time_sequence_list = []
    time_sequence_list = time_sequence_list.strip()  # remove the space
    char_length = len(time_sequence_list)
    buf_ddhhmm = ['0' for s in range(0, 32)]
    buf_SS = ['0' for s in range(0, 32)]
    buf_sss = ['0' for s in range(0, 32)]
    global_minute = 0
    i = 0
    buffer_i = 0
    buffer_k = 0
    buffer_j = 0
    num_of_colons = 0
    dd = 0
    hh = 0
    mm = 0
    SS = 0
    sss = 0

    # DDHHMM:SS:sss or HHMM:SS:sss
    while i < char_length:
        ch = time_sequence_list[i]
        i += 1
        if num_of_colons == 0 and ch != ';' and ch != ':':  # input to buf_ddhhmm until we meet the colon
            buf_ddhhmm[buffer_i] = ch
            buffer_i += 1
        elif num_of_colons == 1 and ch != ':':  # start the Second "SS"
            buf_SS[buffer_k] = ch
            buffer_k += 1
        elif num_of_colons == 2 and ch != ':':  # start the Millisecond "sss"
            buf_sss[buffer_j] = ch
            buffer_j += 1
        
        if ch == ';' or i == char_length:  # start a new time string
            if buffer_i == 4:  # "HHMM"
                # HHMM, 0123
                hh1 = float(buf_ddhhmm[0])  # read each first
                hh2 = float(buf_ddhhmm[1])
                mm1 = float(buf_ddhhmm[2])
                mm2 = float(buf_ddhhmm[3])

                dd = 0
                hh = hh1 * 10 * 60 + hh2 * 60
                mm = mm1 * 10 + mm2
            elif buffer_i == 6:  # "DDHHMM"
                dd1 = float(buf_ddhhmm[0])  # read each first
                dd2 = float(buf_ddhhmm[1])
                hh1 = float(buf_ddhhmm[2])
                hh2 = float(buf_ddhhmm[3])
                mm1 = float(buf_ddhhmm[4])
                mm2 = float(buf_ddhhmm[5])

                dd = dd1 * 10 * 24 * 60 + dd2 * 24 * 60
                hh = hh1 * 10 * 60 + hh2 * 60
                mm = mm1 * 10 + mm2
            
            if num_of_colons == 1 or num_of_colons == 2:
                # SS, 01
                SS1 = float(buf_SS[0])
                SS2 = float(buf_SS[1])
                SS = (SS1 * 10 + SS2) / 60
                sss = 0
            
            if num_of_colons == 2:
                # sss, 012
                sss1 = float(buf_sss[0])
                sss2 = float(buf_sss[1])
                sss3 = float(buf_sss[2])
                sss = (sss1 * 100 + sss2 * 10 + sss3) / 1000

            global_minute = dd + hh + mm + SS + sss
            output_time_sequence_list.append(global_minute)
            # reset the parameters
            buffer_i = 0
            buffer_k = 0
            buffer_j = 0
            num_of_colons = 0
        
        if ch == ':':
            num_of_colons += 1

    return output_time_sequence_list

def g_get_DDHHMM_from_value(value):
    str_DD = ''
    str_HH = ''
    str_MM = ''
    DD_value = int(value / 1440)
    if DD_value > 0 and DD_value < 10:
        str_DD = '0' + str(DD_value)
    elif DD_value >= 10:
        str_DD = str(DD_value)
    HH_value = int((value - DD_value * 1440) / 60)
    if HH_value == 0 and DD_value > 0:
        str_HH = '00'
    elif HH_value > 0 and HH_value < 10:
        str_HH = '0' + str(HH_value)
    elif HH_value >= 10:
        str_HH = str(HH_value)
    MM_value = int(value - DD_value * 1440 - HH_value * 60)
    if MM_value == 0 and HH_value > 0:
        str_MM = '00'
    elif MM_value > 0 and MM_value < 10:
        str_MM = '0' + str(MM_value)
    elif MM_value >= 10:
        str_MM = str(MM_value)
    name = str_DD + str_HH + str_MM
    return name


def g_ReadInputData():
    global g_number_of_nodes
    global g_number_of_road_links
    global g_number_of_agents
    with open('node.csv', 'r') as fp:
        internal_node_seq_no = 0
        lines = fp.readlines()
        temp = lines[0].strip().split(',')
        index_name = temp.index('name')
        index_node_id = temp.index('node_id')
        index_x_corrd = temp.index('x_corrd')
        index_y_coord = temp.index('y_coord')
        for l in lines[1:]:
            l = l.strip().split(',')
            try:
                node = Node()
                node.name = l[index_name]
                node.node_id = int(l[index_node_id])
                # from id to seq no
                g_internal_node_seq_no_dict[node.node_id] = internal_node_seq_no
                # from seq no to id
                g_external_node_id_dict[internal_node_seq_no] = node.node_id
                node.node_seq_no = internal_node_seq_no
                internal_node_seq_no += 1
                node.x_corrd = float(l[index_x_corrd])
                node.y_coord = float(l[index_y_coord])
                g_node_list.append(node)
                g_number_of_nodes += 1
                if g_number_of_nodes % 100 == 0:
                    print('reading {} nodes'.format(g_number_of_nodes))
            except:
                print('Fail to read the input node file.')
        print('number of nodes:{}'.format(g_number_of_nodes))

    with open('road_link.csv', 'r') as fp:
        internal_road_link_seq_no = 0
        lines = fp.readlines()
        temp = lines[0].strip().split(',')
        index_name = temp.index('name')
        index_road_link_id = temp.index('road_link_id')
        index_from_node_id = temp.index('from_node_id')
        index_to_node_id = temp.index('to_node_id')
        index_length = temp.index('length')
        index_display_sequence = temp.index('display_sequence')
        for l in lines[1:]:
            l = l.strip().split(',')
            try:
                link = Link()
                link.name = l[index_name]
                link.road_link_id = int(l[index_road_link_id])
                # from id to seq no
                g_internal_road_link_seq_no_dict[link.road_link_id] = internal_road_link_seq_no
                # from seq no to id
                g_external_road_link_id_dict[internal_road_link_seq_no] = link.road_link_id
                link.from_node_id = int(l[index_from_node_id])
                link.to_node_id = int(l[index_to_node_id])
                link.from_node_seq_no = g_internal_node_seq_no_dict[link.from_node_id]
                link.to_node_seq_no = g_internal_node_seq_no_dict[link.to_node_id]
                link.link_seq_no = internal_road_link_seq_no
                internal_road_link_seq_no += 1
                link.length = int(l[index_length])
                link.display_sequence = int(l[index_display_sequence])  # value starts from 0
                link_key = link.from_node_seq_no * 100000 + link.to_node_seq_no
                g_link_key_to_seq_no_dict[link_key] = link.link_seq_no
                g_road_link_list.append(link)
                g_number_of_road_links += 1
                if g_number_of_road_links % 100 == 0:
                    print('reading {} links'.format(g_number_of_road_links))
            except:
                print('Fail to read the input road link file.')
        print('number of road links:{}'.format(g_number_of_road_links))

        with open('agent.csv', 'r') as fp:
            lines = fp.readlines()
            temp = lines[0].strip().split(',')
            index_agent_id = temp.index('agent_id')
            index_o_node_id = temp.index('o_node_id')
            index_d_node_id = temp.index('d_node_id')
            index_node_sequence = temp.index('node_sequence')
            index_time_sequence = temp.index('time_sequence')
            index_agent_type = temp.index('agent_type')
            for l in lines[1:]:
                l = l.strip().split(',')
                try:
                    agent = Agent()
                    agent.agent_id = int(l[index_agent_id])
                    agent.o_node_id = int(l[index_o_node_id])
                    agent.d_node_id = int(l[index_d_node_id])
                    agent.o_node_seq_no = g_internal_node_seq_no_dict[agent.o_node_id]
                    agent.d_node_seq_no = g_internal_node_seq_no_dict[agent.d_node_id]
                    agent.agent_type = l[index_agent_type]
                    node_sequence_list = l[index_node_sequence].strip().split(';')
                    for k in range(0, len(node_sequence_list)):
                        if node_sequence_list[k] != '':
                            agent.node_sequence.append(g_internal_node_seq_no_dict[int(node_sequence_list[k])])
                    time_sequence_list = l[index_time_sequence]
                    agent.time_sequence = g_time_parser(time_sequence_list)
                    g_agent_list.append(agent)
                    g_number_of_agents += 1
                    if g_number_of_agents % 100 == 0:
                        print('reading {} agents'.format(g_number_of_agents))
                except:
                    print('Fail to read the input agent file.')
            print('number of agents:{}'.format(g_number_of_agents))


def g_draw_space_time_diagram():
    m_link_seq_no = []
    m_link_display_seq = []
    m_node_seq_no = []
    g_yticks_location = []
    g_yticks_name = []
    g_xticks_location = []
    g_xticks_name = []

    color_value = {
        'high-speed': 'r', 
        'normal-speed': 'g', 
        'low-speed':'b',
        'lower-speed':'y'
    }

    for l in range(0, len(g_road_link_list)):
        if g_road_link_list[l].display_sequence != -1:  # -1 do not display; otherwise display
            m_link_seq_no.append(g_road_link_list[l].link_seq_no)
            m_link_display_seq.append(g_road_link_list[l].display_sequence)

    # sort the road links according to the display sequence
    Z = zip(m_link_display_seq, m_link_seq_no)
    Z = sorted(Z)  # sorting in an ascending order by the value of display sequence
    m_link_display_seq, m_link_seq_no = zip(*Z)

    # obtain the y axis location and name
    for i in range(0, len(m_link_seq_no)):
        if i == 0:  # only the left coord
            g_road_link_list[m_link_seq_no[i]].left_corrd = 0
            g_road_link_list[m_link_seq_no[i]].right_corrd = 0 + g_road_link_list[m_link_seq_no[i]].length
            g_yticks_location.append(g_road_link_list[m_link_seq_no[i]].left_corrd)
            g_yticks_location.append(g_road_link_list[m_link_seq_no[i]].right_corrd)
            from_node_seq_no = g_road_link_list[m_link_seq_no[i]].from_node_seq_no
            to_node_seq_no = g_road_link_list[m_link_seq_no[i]].to_node_seq_no
            g_yticks_name.append(g_node_list[from_node_seq_no].name)
            g_yticks_name.append(g_node_list[to_node_seq_no].name)
            m_node_seq_no.append(from_node_seq_no)
            m_node_seq_no.append(to_node_seq_no)
            g_node_list[from_node_seq_no].display_coord = g_road_link_list[m_link_seq_no[i]].left_corrd
            g_node_list[to_node_seq_no].display_coord = g_road_link_list[m_link_seq_no[i]].right_corrd
        else:
            g_road_link_list[m_link_seq_no[i]].left_corrd = g_road_link_list[m_link_seq_no[i - 1]].right_corrd
            g_road_link_list[m_link_seq_no[i]].right_corrd = g_road_link_list[m_link_seq_no[i]].left_corrd + g_road_link_list[m_link_seq_no[i]].length
            g_yticks_location.append(g_road_link_list[m_link_seq_no[i]].right_corrd)
            to_node_seq_no = g_road_link_list[m_link_seq_no[i]].to_node_seq_no
            m_node_seq_no.append(to_node_seq_no)
            g_node_list[to_node_seq_no].display_coord = g_road_link_list[m_link_seq_no[i]].right_corrd
            g_yticks_name.append(g_node_list[to_node_seq_no].name)

    # obtain the nodes and the corresponding node coordinates to dispaly
    for i in range(0, len(g_agent_list)):
        for j in range(0, len(g_agent_list[i].node_sequence)):
            node_seq_no = g_agent_list[i].node_sequence[j]
            if node_seq_no in m_node_seq_no:  # get the available node sequence
                g_agent_list[i].ylist.append(g_node_list[node_seq_no].display_coord)
                g_agent_list[i].xlist.append(g_agent_list[i].time_sequence[j])  # get the available time sequence                

    # draw the space-time diagram
    for i in range(0, len(g_agent_list)):
        agent_type = g_agent_list[i].agent_type
        plt.plot(g_agent_list[i].xlist, g_agent_list[i].ylist, color = color_value[agent_type], linewidth = 1.5)
        plt.text(g_agent_list[i].xlist[0] + 0.1, g_agent_list[i].ylist[0] + 2,\
             '%d' % int(g_agent_list[i].agent_id), ha='center', va= 'bottom', color = color_value[agent_type], weight = 'bold', family = 'Times new roman', fontsize= 12)

    g_ylim_min = 0
    g_ylim_max = g_yticks_location[-1]  # last element
    temp_time_sequence = []
    for i in range(0, len(g_agent_list)):
        temp_time_sequence.append(g_agent_list[i].time_sequence)
        
    g_xlim_min = int(min(min(row) for row in temp_time_sequence))
    g_xlim_max = int(max(max(row) for row in temp_time_sequence)) + g_x_axis_unit

    plt.grid(True)  # show the grid
    plt.ylim(g_ylim_min, g_ylim_max)  # y range
    plt.xlim(g_xlim_min, g_xlim_max)  # x range
    for i in range(g_xlim_min, g_xlim_max + 1, g_x_axis_unit):
        g_xticks_location.append(i)
        name = g_get_DDHHMM_from_value(i)
        g_xticks_name.append(name)
    plt.xticks(g_xticks_location, g_xticks_name, family = 'Times new roman', fontsize= 12)

    plt.yticks(g_yticks_location, g_yticks_name, family = 'Times new roman', fontsize= 12)
    plt.xlabel('Time (HHMM)', family = 'Times new roman', fontsize= 12)
    plt.ylabel('Space (mile)', family = 'Times new roman', fontsize= 12)
    plt.show()


if __name__ == '__main__':
    print('Start reading data...')
    g_ReadInputData()
    print('Finishing reading data...')
    g_draw_space_time_diagram()    
    print('Output results are finished...')