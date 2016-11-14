from timeit import default_timer as timer


class AntiFraud(object):

    def __init__(self):
        self.batch_payment = '../paymo_input/batch_payment.txt'
        self.stream_payment = '../paymo_input/stream_payment.txt'
        self.id_graph = {}

    def create_graph(self):
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
                                id2 : [id1, id3]
                                id1 : [id6, id2]
                                id6 : [id1]
                                id3 : [id2, id4]
                                id4 : [id3]
                                .....
                                idx : [idy, idz, ...]
                            }

            The dictionary (a hash map because of its constant complexity) will save each id as a key and it will have
            a set(so that ids are not repeated) with all the adjacent ids.

        """
        with open(self.batch_payment) as f:
            next(f)  # ignores header
            for trans in f:
                trans_list = trans.split(',')  # trans_list[1] has the first id, trans_list[2] has the second id

                if trans_list[1] in self.id_graph:
                    self.id_graph.get(trans_list[1]).add(trans_list[2])
                else:
                    self.id_graph.update({trans_list[1]: {trans_list[2]}})

                if trans_list[2] in self.id_graph:
                    self.id_graph.get(trans_list[2]).add(trans_list[1])
                else:
                    self.id_graph.update({trans_list[2]: {trans_list[1]}})

    def fraud_detection(self, degree):
        """ This func finds if every user in the txt is connected or not depending on the degree of separation the users
            of the application want """
        result_list=[]
        with open(self.stream_payment) as f:
            next(f)
            for trans in f:
                trans_list = trans.split(',')  # trans_list[1] has the first id, trans_list[2] has the second id
                if len(trans_list) == 5 and self.id_graph.get(trans_list[1]):  # if the user giving the money exists in the graph and the line is correct
                    if self.are_connected(degree, trans_list[1], trans_list[2]):
                        result_list.append("trusted")
                    else:
                        result_list.append("unverified")
                else:
                    result_list.append("unverified")  # this user has never made a transaction, so any transaction will be untrusted,
                                          # should I add it to the graph?
        return result_list
    def are_connected(self, degree, id1, id2):
        """
            This func returns true if the two users have the specified degree of separation or less
            and false if they don't.

            It will have a queue with all the adjacent nodes connected to the node performing the transaction (id1),
            if the node we are looking for (id2) is not in this list it will the func new_queue
            that gets all nodes from the next level in a new list.

        """
        if self.id_graph.get(id1):
            queue = self.id_graph.get(id1)
            depth = 0
            while depth < degree:
                if id2 in queue:
                    return True
                else:
                    depth += 1
                    if depth < degree:  # Don't do extra work
                        queue = self.new_queue(queue)

        return False

    def new_queue(self, queue):
        """ This will create a new queue for the next degree """

        new_queue = set()
        for id1 in queue:
            if self.id_graph.get(id1):
                new_queue.update(self.id_graph.get(id1))
        return new_queue

    def write_to_txt(self, file_name, degree):
        """ This will write the generator to an output file """
        start = timer()
        g = self.fraud_detection(degree)
        end = timer()
        print("Feature completed " + str(end - start))
        with open(file_name, 'w') as f:
            for x in g:
                f.write(str(x)+"\n")
        print("Finished writing to file")

    def main(self):

        # Creates the original graph, in a real life scenario this won't run when reading from a stream
        start1 = timer()
        self.create_graph()
        end1 = timer()
        print("graph creation " + str(end1 - start1))

        # Feature 1: save file with 1 level of separation (adjacent nodes)
        self.write_to_txt("../paymo_output/output_1.txt", 1) # this looks ugly, it should be a var

        # Feature 2: save file with 2 level of separation (adjacent nodes)
        self.write_to_txt("../paymo_output/output_2.txt", 2) # this looks ugly, it should be a var

        # Feature 3: save file with 4 level of separation (adjacent nodes)
        self.write_to_txt("../paymo_output/output_3.txt", 4) # this looks ugly, it should be a var

if __name__ == "__main__":
    AntiFraud().main()



