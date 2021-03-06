import neat

import visualize
from core.dataloader import *
from core.ga_err_functions import feature_sel_err_metab_small, \
    feature_sel_err_metab_large, feature_sel_err_metab_comb, create_node_names
from core.utilities import prompt_num_epochs, BaseGA


# todo make a readme detailing all the specifics used in each algorithm. For
#  example for GA we do not split the dataset, etc. Document everything.

class FeatureSelectionGA:
    """
    This class will implement high level API to call the genetic algorithm
    NEAT and run it as a classifier.

    Loads in the entire dataset. It then uses the entire thing to train and
    uses training accuracy as a measure of fitness.
    """
    output_features = 6
    acc_function = None

    @staticmethod
    def set_output_features(k):
        """
        Tells the class how many output features to manufacture for the RFW
        classifier to use.
        :param k: desired number of features.
        :return: None.
        """
        FeatureSelectionGA.output_features = k

    @staticmethod
    def metabolite_small_dataset():
        """
        Runs the small dataset of OAT1-OAT3.

        The GA will receive all the features together and then use leave one
        out to find its accuracy over given number of epochs.
        :return: None.
        """
        num_epochs = prompt_num_epochs()

        dl = DataLoaderMetabolite()
        train_data, train_labels, header = dl.load_oat1_3_small()

        algo = BaseGA('./configs/metabolite_BI.config',
                      checkpoint_prefix='GA_metab_sm_')

        FeatureSelectionGA.acc_function = feature_sel_err_metab_small

        FeatureSelectionGA.run_session(algo, header, num_epochs)

    @staticmethod
    def metabolite_large_dataset():
        """
        Runs the small dataset of OAT1-OAT3.

        The GA will receive all the features together and then use leave one
        out to find its accuracy over given number of epochs.
        :return: None.
        """
        num_epochs = prompt_num_epochs()

        dl = DataLoaderMetabolite()
        train_data, train_labels, header = dl.load_oat1_3_large()

        algo = BaseGA('./configs/metabolite_BI.config',
                      checkpoint_prefix='GA_metab_lg_')

        FeatureSelectionGA.acc_function = feature_sel_err_metab_large

        FeatureSelectionGA.run_session(algo, header, num_epochs)

    @staticmethod
    def metabolite_combined_dataset():
        """
        Runs the small dataset of OAT1-OAT3.

        The GA will receive all the features together and then use leave one
        out to find its accuracy over given number of epochs.
        :return: None.
        """
        num_epochs = prompt_num_epochs()

        dl = DataLoaderMetabolite()
        train_data, train_labels, header = dl.load_oat1_3_p_combined()

        algo = BaseGA('./configs/metabolite_MULTI.config',
                      checkpoint_prefix='GA_metab_cb_')

        FeatureSelectionGA.acc_function = feature_sel_err_metab_comb

        FeatureSelectionGA.run_session(algo, header, num_epochs)

    @staticmethod
    def run_session(algorithm, header, num_epochs):
        """
        Runs a session for any dataset to do feature engineering.
        :param algorithm: GA object to use to create the session.
        :param header: names of input features.
        :param num_epochs: how many epochs to run for.
        :return: None, will open popups using visualization code.
        """
        conf, pop, stats = algorithm.create_session(num_epochs)
        winner = pop.run(FeatureSelectionGA.fitness, num_epochs)
        # Display the winning genome.
        print('\nBest genome:\n{!s}'.format(winner))
        visualize.draw_net(conf, winner, True,
                           node_names=create_node_names(
                               header, FeatureSelectionGA.output_features))
        visualize.plot_stats(stats, ylog=False, view=True)
        visualize.plot_species(stats, view=True)

    @staticmethod
    def run_genome(conf, genome):
        """
        Runs a single genome. This is a wrapper for async calls from fitness
        function.
        :param conf: configuration object.
        :param genome: genome to run.
        :return: None, adjusts genome fitness in place.
        """
        net = neat.nn.FeedForwardNetwork.create(genome, conf)
        acc = FeatureSelectionGA.acc_function(net)
        # assert 0 <= acc <= 1, 'Got unexpected accuracy of %s' % acc
        genome.fitness = acc

    @staticmethod
    def fitness(genomes, conf):
        """
        Function calls the appropriate error function to find the fitness of
        a given genome. Fitness in our case is defined by the AUC of the genome.
        :param genomes: list of genomes
        :param conf: configuration object for NEAT
        :return: none
        """
        # spawn half as many processes as there are genomes
        # executor = concurrent.futures.ProcessPoolExecutor(5)
        # futures = [executor.submit(FeatureEngineering.run_genome, genome) for
        #            genome in genomes]
        # concurrent.futures.wait(futures)

        # old code
        for gid, genome in genomes:
            FeatureSelectionGA.run_genome(conf, genome)

    @staticmethod
    def view_winner(checkpoint_file_path):
        """
        todo complete this function
        Gets the report for the winner from the checkpoint file pointed to.
        :param checkpoint_file_path: filepath of checkpoint whose winner you
        want to draw.
        :return: none, opens files and writes to disk.
        """

        assert os._exists(checkpoint_file_path), \
            'Enter a valid filename when calling view_winner'
