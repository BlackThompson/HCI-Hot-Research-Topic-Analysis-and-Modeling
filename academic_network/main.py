import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import mpld3
from mpld3 import plugins, utils


def match_name_abbreviation(full_name, abbreviation):
    # 将简写中的每个字母后面添加一个点，以匹配全名中的首字母缩写
    abbreviation_regex = re.escape(abbreviation)
    pattern0 = abbreviation_regex.replace(' ', '[A-Za-z]+ ')
    first_space_index = abbreviation.find(' ')
    pattern1 = abbreviation[:first_space_index + 1] + abbreviation[first_space_index + 1:].replace(' ', '[A-Za-z]+ ')

    pattern0, pattern1 = pattern0[:-1], pattern1[:-1]

    # 使用正则表达式进行匹配
    match0 = re.search(pattern0, full_name, re.IGNORECASE)
    match1 = re.search(pattern1, full_name, re.IGNORECASE)

    if match0 or match1:
        return True
    else:
        return False


def check_abbreviation_in_list(full_name_list, abbreviation):
    for name in full_name_list:
        if match_name_abbreviation(name, abbreviation):
            full_name = name
            return full_name
    return False


def read_excel(path1, path2):
    """
    a temporary function to load data from excel
    """
    data1 = pd.read_excel(path1)
    data2 = pd.read_excel(path2)
    person_url = list(data1['person_url'])
    paper_url = list(data2['url'])
    name_list = list(data1['person_name'])
    citation_list = list(data1['citation_sum'])
    h_list = list(data1['h_index'])
    i10_list = list(data1['i10_index'])
    keyword_list = list(data1['keywords'])
    authors_list = list(data2['authors'])

    num_person = len(name_list)
    ignore_list = []
    not_ignore_list = []
    collab_dict = {}
    collaborations = np.zeros([num_person, num_person])
    for authors in authors_list:
        authors_split = authors.split(', ')
        num_authors = len(authors_split)
        for i in range(num_authors - 1):
            for j in range(i + 1, num_authors):
                if not authors_split[i] in not_ignore_list:
                    if authors_split[i] not in name_list:
                        if authors_split[i] in ignore_list: continue
                        full_name = check_abbreviation_in_list(name_list, authors_split[i])
                        if not full_name:
                            continue
                        else:
                            print("warning: abbreviation found: ", authors_split[i], '<-', full_name)
                            ignore = input("ignore?[y/n]:")
                            if ignore == 'y':
                                ignore_list.append(authors_split[i])
                                continue
                            else:
                                not_ignore_list.append(authors_split[i])
                if not authors_split[j] in not_ignore_list:
                    if authors_split[j] not in name_list:
                        if authors_split[j] in ignore_list: continue
                        full_name = check_abbreviation_in_list(name_list, authors_split[j])
                        if not full_name:
                            continue
                        else:
                            print("warning: abbreviation found: ", authors_split[j], '<-', full_name)
                            ignore = input("ignore?[y/n]:")
                            if ignore == 'y':
                                ignore_list.append(authors_split[j])
                                continue
                            else:
                                not_ignore_list.append(authors_split[j])
                if authors_split[i] + ',' + authors_split[j] in collab_dict:
                    collab_dict[authors_split[i] + ',' + authors_split[j]] += 1
                elif authors_split[j] + ',' + authors_split[i] in collab_dict:
                    collab_dict[authors_split[j] + ',' + authors_split[i]] += 1
                else:
                    collab_dict[authors_split[i] + ',' + authors_split[j]] = 1
    position_mapping = {name: i for name, i in zip(name_list, range(num_person))}

    for key in collab_dict.keys():
        authors = key.split(',')
        first_author, second_author = authors[0], authors[1]
        if first_author in not_ignore_list:
            for name in name_list:
                if match_name_abbreviation(name, first_author):
                    first_author = name
        if second_author in not_ignore_list:
            for name in name_list:
                if match_name_abbreviation(name, second_author):
                    second_author = name
        first_position, second_position = position_mapping[first_author], position_mapping[second_author]
        i, j = min(first_position, second_position), max(first_position, second_position)
        collaborations[i, j] = collab_dict[key]

    keyword_list_handle = [keywords[2:-2].replace("', '", ", ") for keywords in keyword_list]

    return name_list, citation_list, h_list, i10_list, collaborations.astype(
        int), person_url, paper_url, keyword_list_handle


def draw_graph(nodes, citation_list, collaborations, person_url, keyword_list, node_size_factor, edge_width_factor,
               edge_label=False, save=False):
    G = nx.Graph()
    fig, ax = plt.subplots(figsize=(14, 7))

    seed = 23
    num_person = len(nodes)
    edges = []
    collaborations_temp = []
    for i in range(num_person - 1):
        for j in range(i + 1, num_person):
            if collaborations[i, j] == 0:
                continue
            edges.append((nodes[i], nodes[j]))
            collaborations_temp.append(collaborations[i, j])
    collaborations = collaborations_temp
    node_size = np.array(citation_list)
    node_size = ((node_size - np.min(node_size)) / np.max(node_size) + 2 / num_person) * node_size_factor
    edge_width = np.array(collaborations)
    edge_width = ((edge_width - np.min(edge_width)) / np.max(edge_width) + 2 / len(
        set(collaborations))) * edge_width_factor
    node_labels = dict([(nodes[i], nodes[i]) for i in range(num_person)])
    edge_labels = dict(
        [(edges[i], str(collaborations[i])) if collaborations[i] > np.quantile(collaborations, 0.9) else (edges[i], '')
         for i in range(len(edges))])

    caption = [nodes[i] + '<br>cites:' + str(citation_list[i]) + '<br>keywords:' + keyword_list[i] for i in
               range(num_person)]

    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # Draw graph
    pos = nx.spring_layout(G, seed=seed)  # Seed layout for reproducibility
    options = {
        "node_color": "#A0CBE2",
        "node_size": node_size,
        "alpha": 0.5,
        "ax": ax
    }
    scatter = nx.draw_networkx_nodes(G, pos, **options)
    options = {
        "edge_color": collaborations,
        "edge_cmap": plt.cm.Blues,
        "width": edge_width,
        "alpha": 0.6,
        "ax": ax
    }
    nx.draw_networkx_edges(G, pos, **options)
    for node, label in node_labels.items():
        x, y = pos[node]
        plt.text(x, y, label, zorder=0, fontsize=8)
    if edge_label:
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, label_pos=0.4, bbox=dict(alpha=0), ax=ax)

    plugins.connect(fig, TooltipPlugin(scatter, labels=caption, targets=person_url, voffset=10, hoffset=10))

    plt.xticks([])
    plt.yticks([])
    plt.axis('off')

    mpld3.show()
    if save:
        mpld3.save_html(fig, "figure.html")
        # mpld3.save_json(fig, "figure")


class TooltipPlugin(plugins.PluginBase):
    JAVASCRIPT = """
        mpld3.register_plugin("htmltooltip", HtmlTooltipPlugin);
        HtmlTooltipPlugin.prototype = Object.create(mpld3.Plugin.prototype);
        HtmlTooltipPlugin.prototype.constructor = HtmlTooltipPlugin;
        HtmlTooltipPlugin.prototype.requiredProps = ["id"];
        HtmlTooltipPlugin.prototype.defaultProps = {labels:null,
                                                    target:null,
                                                    hoffset:0,
                                                    voffset:10,
                                                    targets:null};
        function HtmlTooltipPlugin(fig, props){
            mpld3.Plugin.call(this, fig, props);
        };

        HtmlTooltipPlugin.prototype.draw = function(){
            var obj = mpld3.get_element(this.props.id, this.fig);
            var labels = this.props.labels;
            var targets = this.props.targets;
            var tooltip = d3.select("body").append("div")
                .attr("class", "mpld3-tooltip")
                .style("position", "absolute")
                .style("z-index", "10")
                .style("visibility", "hidden");

            obj.elements()
                .each(function(d, i) {
                    d3.select(this).attr("data-original-color", d3.select(this).style("fill"));
                })
                .on("mouseover", function(d, i){
                    d3.select(this).transition().duration(50)
                      .style("fill", "blue");
                    tooltip.html(labels[i])
                        .style("visibility", "visible");
                })
                .on("mousemove", function(d, i){
                    tooltip
                    .style("top", d3.event.pageY + this.props.voffset + "px")
                    .style("left",d3.event.pageX + this.props.hoffset + "px");
                }.bind(this))
                .on("mousedown.callout", function(d, i){
                    window.open(targets[i],"_blank");
                })
                .on("mouseout", function(d, i){
                    d3.select(this).transition().duration(200)
                      .style("fill", function() { return d3.select(this).attr("data-original-color"); });
                    tooltip.style("visibility", "hidden");
                });
        };
        """

    def __init__(self, points, labels=None, targets=None,
                 hoffset=0, voffset=10, css=None):
        self.points = points
        self.labels = labels
        self.targets = targets
        self.voffset = voffset
        self.hoffset = hoffset
        self.css_ = css or ""
        if isinstance(points, matplotlib.lines.Line2D):
            suffix = "pts"
        else:
            suffix = None
        self.dict_ = {"type": "htmltooltip",
                      "id": utils.get_id(points, suffix),
                      "labels": labels,
                      "targets": targets,
                      "hoffset": hoffset,
                      "voffset": voffset}


if __name__ == '__main__':
    nodes, citation_list, h_list, i10_list, collaborations, person_url, paper_url, keyword_list = read_excel(
        'Coauthors_Kaiming He.xlsx', 'Kaiming He.xlsx')
    draw_graph(nodes, citation_list, collaborations, person_url, keyword_list, 2500, 10, edge_label=True, save=True)
