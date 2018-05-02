import requests
from collections import defaultdict


class AntiFraud():

    @staticmethod
    def create_graph(url):

        """
            Example graph:
              _____         _____
             | id1 |  ---- | id6 | ...
              -----         -----
                |
                |
              _____         _____        _____
             | id2 |  ---- | id3 | ---- | id4 | ...
              -----         -----        -----

            This method returns a graph structure that looks like this:

                id_graph = {
                                id2 : {id1, id3}
                                id1 : {id6, id2}
                                id6 : {id1}
                                id3 : {id2, id4}
                                id4 : {id3}
                                .....
                                idx : {idy, idz, ...}
                            }

        """

        graph = defaultdict(set)
        r = requests.get(url, stream=True)

        for i, line in enumerate(r.iter_lines()):
            decoded_line = line.decode('utf-8').strip().split(',')
            if len(decoded_line) == 5:
                if decoded_line[1] not in graph:
                    graph[decoded_line[1]] = {(decoded_line[2])}
                else:
                    graph[decoded_line[1]].add(decoded_line[2])

                if decoded_line[2] not in graph:
                    graph[decoded_line[2]] = {decoded_line[1]}
                else:
                    graph[decoded_line[2]].add(decoded_line[1])

        return graph

    @staticmethod
    def classify_simple(graph, url, max_lines):
        r = requests.get(url, stream=True)
        for i, line in enumerate(r.iter_lines()):
            if line and i < max_lines:
                decoded_line = [i.strip() for i in line.decode('utf-8').split(',').strip()]
                if decoded_line[2] in graph[decoded_line[1]]:
                    print(decoded_line[2] + ' in ' + decoded_line[1])
                    print('trusted')

                else:
                    print(decoded_line[2], decoded_line[1])
                    print('untrusted')

            else:
                break

    @staticmethod
    def bfs(graph, nodes, end, n, l=0, ans=False):
        while not ans and l <= n:
            # print(nodes, end)
            if end in nodes:
                return True
            else:
                l += 1
                new_nodes = set()
                for i in nodes:
                    new_nodes.update(graph[i])
                ans = bfs(graph, new_nodes, end, n, l, ans)

        return ans

    @staticmethod
    def classify_bfs(graph, url, nth_degree, max_lines):
        r = requests.get(url, stream=True)
        for i, line in enumerate(r.iter_lines()):
            if line and i < max_lines:
                decoded_line = [i.strip() for i in line.decode('utf-8').split(',')]
                if bfs(graph, [decoded_line[1]], decoded_line[2], nth_degree):
                    print(decoded_line[2] + ' in ' + decoded_line[1])
                    print('trusted')

                else:
                    print(decoded_line[2] + ' in ' + decoded_line[1])
                    print('untrusted')

            else:
                break
