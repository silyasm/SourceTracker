# -*- coding: utf-8 -*-
import os
import time
import unittest
import logging
from configparser import ConfigParser
import inspect

from SourceTracker.SourceTrackerServer import MethodContext
from SourceTracker.authclient import KBaseAuth as _KBaseAuth
from installed_clients.WorkspaceClient import Workspace
from installed_clients.DataFileUtilClient import DataFileUtil
from SourceTracker.SourceTrackerImpl import SourceTracker


class SourceTrackerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        logging.info('setUpClass')

        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('SourceTracker'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'SourceTracker',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = SourceTracker(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

        cls.dfu = DataFileUtil(cls.callback_url)

        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})
        cls.wsId = ret[0]

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def shortDescription(self):
        return None

    def loadMatrix(self):
        if hasattr(self.__class__, 'amplicon_matrix_ref'):
            return self.__class__.amplicon_matrix_ref

        # matrix_file_name = 'test_import.xlsx'
        col_attribute = {'attributes': [{'attribute': 'BODY_SITE', 'source': 'upload'},
                                        {'attribute': 'BarcodeSequence', 'source': 'upload'},
                                        {'attribute': 'Description', 'source': 'upload'},
                                        {'attribute': 'LinkerPrimerSequence', 'source': 'upload'}],
                         'instances': {'Sample1': ['gut', 'CGCTTATCGAGA',
                                                   'human gut', 'CATGCTGCCTCCCGTAGGAGT'],
                                       'Sample2': ['gut', 'CATACCAGTAGC',
                                                   'human gut', 'CATGCTGCCTCCCGTAGGAGT'],
                                       'Sample3': ['gut', 'CTCTCTACCTGT',
                                                   'human gut', 'CATGCTGCCTCCCGTAGGAGT'],
                                       'Sample4': ['skin', 'CTCTCGGCCTGT',
                                                   'human skin', 'CATGCTGCCTCCCGTAGGAGT'],
                                       'Sample5': ['skin', 'CTCTCTACCAAT',
                                                   'human skin', 'CATGCTGCCTCCCGTAGGAGT'],
                                       'Sample6': ['skin', 'CTAACTACCAAT',
                                                   'human skin', 'CATGCTGCCTCCCGTAGGAGT']},
                         'ontology_mapping_method': 'BIOM file'}

        info = self.dfu.save_objects({
            'id': self.wsId,
            'objects': [{'type': 'KBaseExperiments.AttributeMapping',
                         'data': col_attribute,
                         'name': 'test_col_attribute_mapping'}]})[0]

        col_attributemapping_ref = "%s/%s/%s" % (info[6], info[0], info[4])

        self.__class__.col_attributemapping_ref = col_attributemapping_ref
        print('Loaded Col AttributeMapping: ' + col_attributemapping_ref)

        row_attribute = {'attributes': [{'attribute': 'taxonomy', 'source': 'upload'}],
                         'instances': {'GG_OTU_1': ['Bacteria;'],
                                       'GG_OTU_2': ['Bacteria;WOR-1;;;;Genera Incertae Sedis;'],
                                       'GG_OTU_3': ['Bacteria;Proteobacteria;' +
                                                    'Gammaproteobacteria;Burkholderiales;' +
                                                    'Comamonadaceae;Variovorax;'],
                                       'GG_OTU_4': ['Bacteria;Proteobacteria;' +
                                                    'Gammaproteobacteria;Pseudomonadales;' +
                                                    'Pseudomonadaceae;Pseudomonas;'],
                                       'GG_OTU_5': ['Bacteria;Proteobacteria;' +
                                                    'Gammaproteobacteria;Burkholderiales;' +
                                                    'Burkholderiaceae;Cupriavidus;']},
                         'ontology_mapping_method': 'BIOM file'}

        info = self.dfu.save_objects({
            'id': self.wsId,
            'objects': [{'type': 'KBaseExperiments.AttributeMapping',
                         'data': row_attribute,
                         'name': 'test_row_attribute_mapping'}]})[0]

        row_attributemapping_ref = "%s/%s/%s" % (info[6], info[0], info[4])

        self.__class__.row_attributemapping_ref = row_attributemapping_ref
        print('Loaded Row AttributeMapping: ' + row_attributemapping_ref)

        matrix_data = {'amplicon_type': '16S',
                       'attributes': {'generated_by': 'QIIME revision XYZ'},
                       'clustering_cutoff': 0.3,
                       'clustering_method': 'clustering_method',
                       'col_attributemapping_ref': col_attributemapping_ref,
                       'col_mapping': {'Sample1': 'Sample1',
                                       'Sample2': 'Sample2',
                                       'Sample3': 'Sample3',
                                       'Sample4': 'Sample4',
                                       'Sample5': 'Sample5',
                                       'Sample6': 'Sample6'},
                       'data': {'col_ids': ['Sample1', 'Sample2', 'Sample3', 'Sample4',
                                            'Sample5', 'Sample6'],
                                'row_ids': ['GG_OTU_1', 'GG_OTU_2', 'GG_OTU_3',
                                            'GG_OTU_4', 'GG_OTU_5'],
                                'values': [[0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
                                           [5.0, 1.0, 0.0, 2.0, 3.0, 1.0],
                                           [0.0, 0.0, 1.0, 4.0, 2.0, 0.0],
                                           [2.0, 1.0, 1.0, 0.0, 0.0, 1.0],
                                           [0.0, 1.0, 1.0, 0.0, 0.0, 0.0]]},
                       'description': 'OTU data',
                       'row_attributemapping_ref': row_attributemapping_ref,
                       'row_mapping': {'GG_OTU_1': 'GG_OTU_1',
                                       'GG_OTU_2': 'GG_OTU_2',
                                       'GG_OTU_3': 'GG_OTU_3',
                                       'GG_OTU_4': 'GG_OTU_4',
                                       'GG_OTU_5': 'GG_OTU_5'},
                       'scale': 'raw',
                       'search_attributes': ['generated_by|QIIME revision XYZ'],
                       'sequencing_file_handle': 'KBH_670996',
                       'sequencing_instrument': 'Illumina Genome Analyzer',
                       'sequencing_technology': 'Illumina',
                       'target_gene': '16S',
                       'target_subfragment': ['V1'],
                       'taxon_calling_method': ['clustering']}

        info = self.dfu.save_objects({'id': self.wsId,
                                      'objects': [{'type': 'KBaseMatrices.AmpliconMatrix',
                                                   'data': matrix_data,
                                                   'name': 'test_AmpliconMatrix'}]})[0]

        amplicon_matrix_ref = "%s/%s/%s" % (info[6], info[0], info[4])

        self.__class__.amplicon_matrix_ref = amplicon_matrix_ref
        print('Loaded AmpliconMatrix: ' + amplicon_matrix_ref)

        # load associated matrix
        matrix_data = {'amplicon_type': '16S',
                       'attributes': {'generated_by': 'QIIME revision XYZ'},
                       'clustering_cutoff': 0.3,
                       'clustering_method': 'clustering_method',
                       'col_attributemapping_ref': col_attributemapping_ref,
                       'col_mapping': {'Sample1': 'Sample1',
                                       'Sample2': 'Sample2',
                                       'Sample3': 'Sample3',
                                       'Sample4': 'Sample4',
                                       'Sample5': 'Sample5',
                                       'Sample6': 'Sample6'},
                       'data': {'col_ids': ['Sample1', 'Sample2', 'Sample3', 'Sample4',
                                            'Sample5', 'Sample6'],
                                'row_ids': ['GG_OTU_1', 'GG_OTU_2', 'GG_OTU_3',
                                            'GG_OTU_4', 'GG_OTU_5'],
                                'values': [[0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
                                           [5.0, 1.0, 0.0, 2.0, 3.0, 1.0],
                                           [0.0, 0.0, 1.0, 4.0, 2.0, 0.0],
                                           [2.0, 1.0, 1.0, 0.0, 0.0, 1.0],
                                           [0.0, 1.0, 1.0, 0.0, 0.0, 0.0]]},
                       'description': 'OTU data',
                       'row_attributemapping_ref': row_attributemapping_ref,
                       'row_mapping': {'GG_OTU_1': 'GG_OTU_1',
                                       'GG_OTU_2': 'GG_OTU_2',
                                       'GG_OTU_3': 'GG_OTU_3',
                                       'GG_OTU_4': 'GG_OTU_4',
                                       'GG_OTU_5': 'GG_OTU_5'},
                       'scale': 'raw',
                       'search_attributes': ['generated_by|QIIME revision XYZ'],
                       'sequencing_file_handle': 'KBH_670996',
                       'sequencing_instrument': 'Illumina Genome Analyzer',
                       'sequencing_technology': 'Illumina',
                       'target_gene': '16S',
                       'target_subfragment': ['V1'],
                       'taxon_calling_method': ['clustering']}

        info = self.dfu.save_objects({
            'id': self.wsId,
            'objects': [{'type': 'KBaseMatrices.AmpliconMatrix',
                         'data': matrix_data,
                         'name': 'test_associated_AmpliconMatrix'}]})[0]

        asso_matrix_ref = "%s/%s/%s" % (info[6], info[0], info[4])

        self.__class__.asso_matrix_ref = asso_matrix_ref
        print('Loaded Associated AmpliconMatrix: ' + asso_matrix_ref)

    def start_test(self):
        testname = inspect.stack()[1][3]
        print('\n*** starting test: ' + testname + ' **')

    def test_SourceTracker(self):
        self.start_test()
        self.loadMatrix()

        # test only taxonomy
        ret = self.serviceImpl.run_SourceTracker(
            self.ctx, {
                'workspace_name': self.wsName,
                'amplicon_matrix_ref': self.amplicon_matrix_ref,
                'tax_field': 'taxonomy',
                'threshold': 0.005,
            })[0]

        self.assertTrue('report_ref' in ret)
        self.assertTrue('report_name' in ret)

        # test with grouping
        ret = self.serviceImpl.run_SourceTracker(
            self.ctx, {
                'workspace_name': self.wsName,
                'amplicon_matrix_ref': self.amplicon_matrix_ref,
                'tax_field': 'taxonomy',
                'threshold': 0.005,
                'sink_or_sample': 'BODY_SITE',
            })[0]

        self.assertTrue('report_ref' in ret)
        self.assertTrue('report_name' in ret)

        # test with ordering
        ret = self.serviceImpl.run_SourceTracker(
            self.ctx, {
                'workspace_name': self.wsName,
                'amplicon_matrix_ref': self.amplicon_matrix_ref,
                'tax_field': 'taxonomy',
                'threshold': 0.005,
                'sink_or_sample': 'BODY_SITE',
                'associated_matrix_obj_ref': self.asso_matrix_ref,
                'associated_matrix_row': 'GG_OTU_2',
                'ascending': 0
            })[0]

        self.assertTrue('report_ref' in ret)
        self.assertTrue('report_name' in ret)
