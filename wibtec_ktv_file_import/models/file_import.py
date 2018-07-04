# -*- coding: utf-8 -*-
import logging
import csv

from odoo import api, fields, models
from odoo import tools
from odoo import os

_logger = logging.getLogger(__name__)

#Linux
SEP = '//'

#windows
#SEP = '\\'

                       
FILE_COLS = [
            'db_id', 'konto_id', 'auftraggeber_konto', 'auftraggeber_blz',
            'auftraggeber_name', 'betrag', 'waehrung', 'zweck', 'zweck2', 'zweck3',
            'zusatzinformation', 'buchungsdatum', 'valuta', 'saldo', 'primanota',
            'art', 'art_erw', 'kunden_referenz', 'kommentar', 'umsatztyp_id',
            'erfassungsreferenz', 'gvcode', 'institutsreferent', 'ist_storno',
            'orig_betrag', 'orig_waehrung', 'partner_name', 'partner_konto',
            'partner_blz', 'db_eintragsdatum', 'db_quelle', 'db_hash_in_quelle',
            'db_statusflags', 'db_kundenkonto_zuordnung', 'abrufdatum'
            ]

class FileImport(models.Model):
    _name = 'wibtec_ktv.file_import'
    _description = 'File import'
    _order = 'create_date DESC'

    ORDERS_FOUND = []
    ORDERS_SAVED = []
    
    name = fields.Char('File', required=True)
    description = fields.Text('Description', required=True)
    status = fields.Selection([('ok','OK'),('nok','NOK')], 'Status', required=True)

   
    @api.model
    def read_files(self):
        file_path = self.get_file_path()
        
        if not os.path.isdir(file_path):
            try:
                os.makedirs(file_path, exist_ok=True)
                for a in ['ok','nok']:
                    aux = file_path + SEP + a
                    if not os.path.isdir(aux):
                        os.makedirs(aux, exist_ok=True)
            except Exception as e:
                self.create_log(file, str(e), 'nok')
                return False
        
        if os.path.isdir(file_path):
            files = [file_path + SEP + f for f in os.listdir(file_path)\
                            if os.path.isfile(os.path.join(file_path, f))]
            for f in files:
                if f.endswith('.csv'):
                    self.process_file(f)


    def process_file(self, file=False):
        _logger.info("Processing %s" % file)

        self.ORDERS_FOUND = []
        self.ORDERS_SAVED = []

        try:
            ifile = open(file, 'r')
            reader = csv.reader(ifile, delimiter=';')
        except Exception as e:
            self.create_log(file, str(e), 'nok')
            self.move_file(file, 'nok')
            return False

        msg_error = []
        order_id_col = False
        #order_details = {'api_order': False}
        order_details = {}
        current_order = False
        rownum = 0

        for row in reader:
            if rownum == 0:
                header = row

                # Get the column with the order number
                aux_colnum = 0
                posFound = False
                for col in row:
                    if col == 'db_id':
                        order_id_col = aux_colnum
                        posFound = True
                        break
                    aux_colnum += 1
                    
                #No column was found with the order number
                if not posFound:
                    self.create_log(file, 'No order number was found', 'nok')
                    self.move_file(file, 'nok')
                    return False
            else:
                if row[order_id_col] != current_order:
                    self.ORDERS_FOUND.append(row[order_id_col])
                
                    # Save previous order
                    if order_details:
                        #order_details['order_lines'] = order_lines
                        res_create = self.save_info(order_details)
                        if res_create['error']:
                            msg_error.append('%s could not be saved => %s ' % (current_order, res_create['message']))
                        else:
                            msg_error.append('%s SAVED ' % current_order)
                            
                    # Reset variables
                    #order_details = {'api_order': False}
                    #order_lines = []
                    current_order = row[order_id_col]

                colnum = 0
                #order_lines.append({})

                for col in row:
                    col_name = header[colnum]
                    if col_name in FILE_COLS:
                        order_details[col_name] = col
                    elif col_name not in msg_error:
                        msg_error.append(col_name)
                    colnum += 1

            rownum += 1

        # Save the last order
        if order_details:
            #order_details['order_lines'] = order_lines
            res_create = self.save_info(order_details)
            if res_create['error']:
                msg_error.append('%s could not be saved => %s ' % (current_order, res_create['message']))
            else:
                msg_error.append('%s SAVED ' % current_order)

        if msg_error:
            msg_error = '%s' % ','.join(msg_error)

        ifile.close()

        if not rownum:
            self.create_log(file, 'No lines found', 'nok')
            self.move_file(file, 'nok')
        else:
            aux = 'Processed'
            if msg_error:
                aux += '\n' + msg_error
            self.create_log(file, aux, 'ok')
            self.move_file(file, 'ok')

        # Enviar EMAIL???
        _logger.info("************************************")
        _logger.info("ORDER IMPORT")
        _logger.info("************************************")
        _logger.info("Found: %s / Saved: %s" % (len(self.ORDERS_FOUND), len(self.ORDERS_SAVED)))
        _logger.info(self.ORDERS_FOUND)
        _logger.info(self.ORDERS_SAVED)
        _logger.info("************************************")

    def save_info(self, order=False):
        if order:
            res = self.env['wibtec_ktv.file_import_aux'].create(order)
            try:
                aux = res['id']
                self.ORDERS_SAVED.append(order['db_id'])
                res = {'error': 0, 'message': ''}

            except Exception as e:
                res = {'error': 1, 'message': e}
                _logger.info(e)
                pass
        else:
            res = {'error': 1, 'message': 'Invalid movement'}
        return res


    def create_log(self, name=False, description='', status=False):
        if name and description and status:
            self.create({
                        'name': name.split(SEP)[-1], 
                        'description': description, 
                        'status': status
                        })

    def move_file(self, file=False, status=False):
        # for testing purposes, we don't move the file
        #return False
        if file and status:
            try:
                new_place = file.split(SEP)
                new_place[-1] = status + SEP + new_place[-1]
                os.rename(file, SEP.join(new_place))
            except Exception as e:
                self.create_log(file, str(e), 'nok')

    def get_file_path(self):
        IRConfig = self.env['ir.config_parameter'].sudo()
        file_path = IRConfig.get_param('wibtec_ktv_import.file_path')
        if not file_path:
            IRConfig.set_param('wibtec_ktv_import.file_path', '/odoo/donations/')
            file_path = IRConfig.get_param('wibtec_ktv_import.file_path')
        return file_path
