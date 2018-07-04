# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FileImportAux(models.Model):
    _name = 'wibtec_ktv.file_import_aux'
    _description = 'Auxiliary table for importing bank statements'
    _rec_name = 'db_id'
    _order = 'db_id DESC'
    
    db_id = fields.Char('DB ID', help='primary key in old database (DB)')
    konto_id = fields.Integer('Konto', 
                                help='primary key of corresponding bank-account in old DB')
    auftraggeber_konto = fields.Char('Auftraggeber konto',
                                help='IBAN in case it is a normal bank-account, npfaa (not present for all accounts)')
    auftraggeber_blz = fields.Char('Auftraggeber blz',
                                help='BIC in case it is a normal bank-account, not present for all accounts')
    auftraggeber_name = fields.Char('Auftraggeber name',
                                help='Name of account owner, that''s usually us, npfaa')
    betrag = fields.Char('Betrag',
                                help='Amount of transaction')
    waehrung = fields.Char('Waehrung',
                                help='Currency of transaction')
                      
    #purpose-lines as given by the other party
    zweck = fields.Char('Zweck')
    zweck2 = fields.Char('Zweck')
    zweck3 = fields.Char('Zweck')

    zusatzinformation = fields.Char('Zusatzinformation', help='Extra information')
    buchungsdatum = fields.Char('Buchungsdatum', help='Booking date')
    valuta = fields.Char('Valuta', help='Availability date')
    saldo = fields.Char('Saldo', help='Balance after this transaction , npfaa')
    primanota = fields.Char('Primanota', help='stack number of book entry, npfaa')
    art = fields.Char('Art')
    art_erw = fields.Char('Art erw')
    kunden_referenz = fields.Char('Kunden referenz')
    kommentar = fields.Char('Kommentar', help='Commentary from bank')
    umsatztyp_id = fields.Char('umsatztyp_id')
    erfassungsreferenz = fields.Char('erfassungsreferenz', help='Acquisition-reference bank')
    gvcode = fields.Char('Gvcode', help='MT940 purpose code; npfaa')
    institutsreferent = fields.Char('Institutsreferent', help='transaction reference id at bank')
    ist_storno = fields.Boolean('Ist storno')
    orig_betrag = fields.Char('Original betrag', help='Original currency from partner / npfaa')
    orig_waehrung = fields.Char('Original waehrung', help='Original amount  from partner / npfaa')
    partner_name = fields.Char('Partner name', help='name of other party') 
    partner_konto = fields.Char('Partner konto', help='Account IBAN of other party')
    partner_blz = fields.Char('Partner blz', help='Account BIC of other party')
    db_eintragsdatum = fields.Char('DB Eintragsdatum', help='Ignore, DB entry date')
    db_quelle = fields.Char('DB Quelle', help='Ignore, provider/technical source of data')
    db_hash_in_quelle = fields.Char('DB hash in quelle', 
                                    help="Ignore, unique value for each line (within konto_id and update-date-range),\
                                    for faster collision detection and updates")
    db_statusflags = fields.Char('DB Statusflags')
    db_kundenkonto_zuordnung = fields.Char('DB kundenkonto zuordnung')
    abrufdatum = fields.Char('Abrufdatum')
    
    state = fields.Selection(
                            [('draft','Draft'),('migrated','Migrated')],
                            default='draft',
                            string='State')
    
    """
    COLOCAR UMA ASSOCIAÇÃO AO MOVIMENTO CONTABILÍSTICO A SER CRIADO!!!
    """
    
    
    
    _sql_constraints = [('Unique ID', 'unique(db_id)','The id already exists')]