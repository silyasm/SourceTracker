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
import numpy as np
import pandas as pd
import SourceTracker.utils.gibbs
import SourceTracker.utils.sourcetrackerUtils
import SourceTracker.utils._gibbs_defaults

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
    VERSION = "0.0.3"
    GIT_URL = "https://github.com/silyasm/SourceTracker"
    GIT_COMMIT_HASH = "a26f8d172c6c9de998d150fced2cc95b69679795"

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
        #should seprtate out sink and source samples into seperate dfs
            if sample.[****] == params['sink_label']:
            #Want to check if sample type field is the same as sink. **** should be the index for just sample type field
                sink_otus.append('amplicon_matrix_ref'.loc[sample.[----]])
                # Place corresponding column in amplicon matrix in the sink array. ---- should be the field with the sample ID
            if sample.[****] == params['source_label']:
            #Want to check if sample type field is the same as source. **** should be the index for just sample type field
                source_otus.append('amplicon_matrix_ref'.loc[sample.[----]])
                # Place corresponding column in amplicon matrix in the source array. ---- should be the field with the sample ID
            else:
                raise ValueError('Label' + sample + 'was not recognised as sink nor sample')
        
        alpha1 = .01
        alpha2 = .001
        beta = 10
        restarts = 5
        draws_per_restart = 1
        burnin = 2
        delay = 2
        source_df = pd.Dataframe([source_otus])
        sink_df = pd.Dataframe([sink_otus])

        mpm, mps, fas = gibbs(source_df, sink_df, alpha1, alpha2, beta,
                                  restarts, draws_per_restart, burnin, delay,
                                  create_feature_tables=True)

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
