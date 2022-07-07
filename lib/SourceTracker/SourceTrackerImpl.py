# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import uuid
from SourceTracker.TAUtils import run
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.DataFileUtilClient import DataFileUtil
from importlib.metadata import metadata
from itertools import accumulate
import random
from random import randrange, sample
from re import A
import pandas
import numpy as np
from IPython.display import display
import csv

#END_HEADER


class SourceTracker:
    '''
    Module Name:
    SourceTracker

    Module Description:
    A KBase module: SourceTracker
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.2"
    GIT_URL = "https://github.com/silyasm/SourceTracker"
    GIT_COMMIT_HASH = "91de93bbe30cab0f1da08c3eac80b1e9aa9827b7"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.token = os.environ['KB_AUTH_TOKEN']
        self.wsURL = config['workspace-url']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_SourceTracker(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of type "SourceTrackerInput" -> structure:
           parameter "workspace_name" of String, parameter "workspace_id" of
           Long, parameter "amplicon_matrix_ref" of String, parameter
           "attri_mapping_ref" of String, parameter "threshold" of Double,
           parameter "taxonomy_level" of Long, parameter "grouping_label" of
           mapping from String to String, parameter "sink_label" of String,
           parameter "sample_type" of String, parameter "source_label" of
           String, parameter "ascending" of Long
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_SourceTracker
        for name in ['sink_label', 'source_label']:
            if name not in params['source_type']:
                raise ValueError('Parameter "' + name + '" is required but missing')
        #for type in params['sample_type']:
        #   if not isinstance(type == params['sink_label'] and type == params['source_label']
        #       raise ValueError('Label "' + type + '" does not match to sink or source label')
        logging.info('start run_SourceTracker with:\n{}'.format(params))

        # extract params
        # do some transformations against narrative ui

        amplicon_matrix_ref = params['amplicon_matrix_ref']
        sample_type = params['sample_type']
        cutoff = params.get('threshold', 0.005)
        grouping_label = params.get('sink_label')
        source_label = params.get('source_label')
        ascending = params.get('ascending', 1)
        self.dfu = DataFileUtil(self.callback_url)

        html_link, warnning = run(amp_id=amplicon_matrix_ref,
                                  sample_type=sample_type, cutoff=cutoff,
                                  grouping_label=grouping_label,
                                  dfu=self.dfu, scratch=self.shared_folder,
                                  source_label=source_label,
                                  ascending=ascending)
        for sample in params['sample_type']:
            if sample. == params['sink_label']:
                sink_otus.append('amplicon_matrix_ref'.loc['sample'])
        
        otuRowsStrings = []
        with open('amplicon_matrix_ref', 'r') as file:
            csvreader = csv.reader(file)
            sources = next(csvreader)
            for row in csvreader:
                otuRowsStrings.append(row)
        OTUs = []
        abundanceData = []
        for row in otuRowsStrings:
            OTUs.append(row.pop(0))
            row = [int(i) for i in row]
            abundanceData.append(row)
        sources.remove('')

        table_otu = pandas.DataFrame(data = abundanceData, columns=[sources], index=[OTUs])
        #display(table_otu)

        table_p_tv = table_otu.loc[table_otu.index].div(table_otu.sum(axis=0), axis=1)
        #display(table_p_tv)

        sink_otu_sources = []
        for x in range(len(OTUs)):
            sink_otu_sources.append(randrange(1, len(OTUs)))

        table_otu_reference = pandas.DataFrame(data=[sink_otu_sources], columns=[OTUs], index= ['Random Sources'])
        #display(table_otu_reference)

        def roll(probs):
            cumulativeWeights = list(accumulate(probs))
            position = random.random()
            for side, endPosition in enumerate(cumulativeWeights):
                if position < endPosition:
                    return side + 1

        predictedSources = []
        p_tv = []

        for i in OTUs:
            p_v = np.bincount(sink_otu_sources, minlength=3)[1:] / float(len(sink_otu_sources))
            p_tv = np.array([(table_p_tv.at[i, sources[0]])])
            comboProbability = p_tv * p_v
            prob = comboProbability / comboProbability.sum()
            predictedSource = roll(prob)
            sink_otu_sources[i] = predictedSource
            predictedSources.append(predictedSource)
        table_prediction = pandas.DataFrame(data=[sink_otus, sink_otu_sources], index=['OTU', 'Predicted Source'])
        return(table_prediction)

        report_client = KBaseReport(self.callback_url, token=self.token)
        report_name = "SourceTracker_report_" + str(uuid.uuid4())
        report_info = report_client.create_extended_report({
            'direct_html_link_index': 0,
            'html_links': [html_link],
            'report_object_name': report_name,
            'warnings': [warnning],
            'workspace_name': params['workspace_name']
        })
        output = {
            'report_ref': report_info['ref'],
            'report_name': report_info['name'],
        }

        #END run_SourceTracker

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_SourceTracker return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
