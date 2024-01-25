from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract, text
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from babel.numbers import format_currency
import dash
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Output, Input, State
from datetime import datetime, timedelta
import pandas as pd
import tensorflow as tf

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@192.168.0.13/nordestina'
app.config['SQLALCHEMY_BINDS'] = {'nordestina': 'mysql://root@192.168.0.13/nordestina', 'sice': 'mysql://root@192.168.0.13/sice'}
app.config['SECRET_KEY'] = 'nordestina'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    __bind_key__ = 'nordestina'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    nivel = db.Column(db.Integer, nullable=False, default = 3)

class Dados_vendas(db.Model):
    __tablename__ = 'dados_vendas'
    __bind_key__ = 'nordestina'
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer)
    mes = db.Column(db.Integer)
    vendedor = db.Column(db.String(255))
    totalbruto = db.Column(db.Float(precision=2))
    desconto = db.Column(db.Float(precision=2))
    total = db.Column(db.Float(precision=2))
    devolucaovenda = db.Column(db.Float(precision=2))
    atendimentos = db.Column(db.Integer)
    CA = db.Column(db.Float(precision=2))
    CH = db.Column(db.Float(precision=2))
    CR = db.Column(db.Float(precision=2))
    DH = db.Column(db.Float(precision=2))
    DV = db.Column(db.Float(precision=2))
    FI = db.Column(db.Float(precision=2))
    FN = db.Column(db.Float(precision=2))
    PD = db.Column(db.Float(precision=2))
    RN = db.Column(db.Float(precision=2))
    RV = db.Column(db.Float(precision=2))
    Se = db.Column(db.Float(precision=2))
    
    @classmethod
    def dados_ia(cls):
        dados = cls.query.all()
        colunas = ['ano', 'mes', 'totalbruto', 'desconto', 'total', 'devolucaovenda']
        dados_df = pd.DataFrame([(d.ano, d.mes, d.totalbruto, d.desconto, d.total, d.devolucaovenda)for d in dados], 
                                columns=colunas)

        return dados_df
    
    @classmethod
    def get_all(cls):
        dados = cls.query.all()
        df = pd.DataFrame([(d.id, d.ano, d.mes, d.vendedor, d.totalbruto, d.desconto, d.total, d.devolucaovenda,
                            d.atendimentos, d.CA, d.CH, d.CR, d.DH, d.DV, d.FI, d.FN, d.PD, d.RN, d.RV, d.Se)
                           for d in dados],
                          columns=['id', 'ano', 'mes', 'vendedor', 'totalbruto', 'desconto', 'total', 'devolucaovenda',
                                   'atendimentos', 'CA', 'CH', 'CR', 'DH', 'DV', 'FI', 'FN', 'PD', 'RN', 'RV', 'Se'])

        return df
    
    @classmethod
    def pesquisa(cls, ano, mes, vendedor):
        # Consulta para verificar a existência dos dados
        resultado = cls.query.filter_by(ano=ano, mes=mes, vendedor=vendedor).first()
        return resultado is not None
    
    @classmethod
    def update(cls, ano, mes, vendedor, totalbruto, desconto, total, devolucaovenda, atendimentos, CA, CH, CR, DH, DV, FI, FN, PD, RN, RV, Se):
        if Dados_vendas.pesquisa(ano=ano, mes=mes, vendedor=vendedor):
            venda = cls.query.filter_by(ano = ano, mes = mes, vendedor = vendedor).first()
            if venda:
                venda.totalbruto = totalbruto
                venda.desconto = desconto
                venda.total = total
                venda.devolucaovenda = devolucaovenda
                venda.atendimentos = atendimentos
                venda.CA = CA
                venda.CH = CH
                venda.CR = CR
                venda.DH = DH
                venda.DV = DV
                venda.FI = FI
                venda.FN = FN
                venda.PD = PD
                venda.RN = RN
                venda.RV = RV
                venda.Se = Se
                db.session.commit()
                return True
            return False
        
        else:
            Dados_vendas.create(ano, mes, vendedor, totalbruto, desconto, total, devolucaovenda, atendimentos, CA, CH, CR, DH, DV, FI, FN, PD, RN, RV, Se)
        
    @classmethod
    def create(cls, ano, mes, vendedor, totalbruto, desconto, total, devolucaovenda, atendimentos, CA, CH, CR, DH, DV, FI, FN, PD, RN, RV, Se):
        nova_venda = cls(
            ano=ano,
            mes=mes,
            vendedor=vendedor,
            totalbruto=totalbruto,
            desconto=desconto,
            total=total,
            devolucaovenda=devolucaovenda,
            atendimentos=atendimentos,
            CA=CA,
            CH=CH,
            CR=CR,
            DH=DH,
            DV=DV,
            FI=FI,
            FN=FN,
            PD=PD,
            RN=RN,
            RV=RV,
            Se=Se
        )
        db.session.add(nova_venda)
        try:
            db.session.commit()
            return True
        except Exception as e:
            print(f"Erro ao criar venda: {e}")
            db.session.rollback()
            return False

class Contdocs_sice(db.Model):
    __tablename__ = 'contdocs'
    __bind_key__ = 'sice'
    documento = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date)
    hora = db.Column(db.String)
    totalbruto = db.Column(db.Float)
    desconto = db.Column(db.Float)
    encargos = db.Column(db.Float)
    total = db.Column(db.Float)
    tipopagamento = db.Column(db.String)
    vendedor = db.Column(db.String)
    codigocliente = db.Column(db.Integer)
    operador = db.Column(db.String)
    CodigoFilial = db.Column(db.String)
    custos = db.Column(db.Float)
    devolucaovenda = db.Column(db.Float)
    
    @classmethod
    def obter_dados_por_ano_mes(cls, ano, mes):
        dados_filtrados = cls.query.filter(
            extract('year', cls.data) == ano,
            extract('month', cls.data) == mes
        ).all()

        colunas = ['documento', 'data', 'hora', 'totalbruto', 'desconto', 'encargos', 'total', 'tipopagamento', 'vendedor', 'codigocliente', 'operador', 'CodigoFilial', 'custos', 'devolucaovenda']
        dados_df = pd.DataFrame([(getattr(item, col) for col in colunas) for item in dados_filtrados], columns=colunas)

        return dados_df
    
    @classmethod
    def get_data(cls, documento):
        return cls.query.filter_by(documento = documento).first().data
    
    @classmethod
    def get_hora(cls, documento):
        return cls.query.filter_by(documento=documento).first().hora

    @classmethod
    def get_totalbruto(cls, documento):
        return cls.query.filter_by(documento=documento).first().totalbruto

    @classmethod
    def get_desconto(cls, documento):
        return cls.query.filter_by(documento=documento).first().desconto

    @classmethod
    def get_encargos(cls, documento):
        return cls.query.filter_by(documento=documento).first().encargos

    @classmethod
    def get_total(cls, documento):
        return cls.query.filter_by(documento=documento).first().total

    @classmethod
    def get_tipopagamento(cls, documento):
        return cls.query.filter_by(documento=documento).first().tipopagamento

    @classmethod
    def get_vendedor(cls, documento):
        return cls.query.filter_by(documento=documento).first().vendedor

    @classmethod
    def get_codigocliente(cls, documento):
        return cls.query.filter_by(documento=documento).first().codigocliente

    @classmethod
    def get_operador(cls, documento):
        return cls.query.filter_by(documento=documento).first().operador

    @classmethod
    def get_CodigoFilial(cls, documento):
        return cls.query.filter_by(documento=documento).first().CodigoFilial

    @classmethod
    def get_custos(cls, documento):
        return cls.query.filter_by(documento=documento).first().custos

    @classmethod
    def get_devolucaovenda(cls, documento):
        return cls.query.filter_by(documento=documento).first().devolucaovenda
              
class Vendedores_sice(db.Model):
    __tablename__ = 'vendedores'
    __bind_key__ = 'sice'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(3))
    nome = db.Column(db.String(255))

class Vendedores_nordepy(db.Model):
    __tablename__ = 'vendedores'
    __bind_key__ = 'nordestina'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(3))
    nome = db.Column(db.String(255))
    status_vendedor = db.Column(db.Boolean, default=False)
    meta_vendedor =  db.Column(db.Float(precision=2), default=00.00)
    
    @classmethod
    def get_nome_codigo(cls, codigo):
        vendedor = cls.query.filter_by(codigo=codigo).first()
        if vendedor:
            return vendedor.nome
        else:
            return codigo

    @classmethod
    def get_nome_id(cls, id):
        return cls.query.filter_by(id=id).first().nome

    @classmethod
    def get_status_codigo(cls, codigo):
        return cls.query.filter_by(codigo=codigo).first().status_vendedor

    @classmethod
    def get_status_id(cls, id):
        return cls.query.filter_by(id=id).first().status_vendedor

    @classmethod
    def get_meta_codigo(cls, codigo):
        return cls.query.filter_by(codigo=codigo).first().meta_vendedor

    @classmethod
    def get_meta_id(cls, id):
        return cls.query.filter_by(id=id).first().meta_vendedor

    @classmethod
    def update(cls, id, codigo, nome, status, meta):
        vendedor = cls.query.filter_by(id=id).first()
        if vendedor:
            vendedor.codigo = codigo
            vendedor.nome = nome
            vendedor.status_vendedor = status
            vendedor.meta_vendedor = meta
            db.session.commit() 
            return True
        return False
    
    @classmethod
    def update_status_meta(cls, id, status, meta):
        vendedor = cls.query.filter_by(id=id).first()
        
        if vendedor:
            vendedor.status_vendedor = status
            vendedor.meta_vendedor = meta
            db.session.commit()
            return True
        return False
    
    @classmethod
    def create(cls, id, codigo, nome, status, meta):
        novo_vendedor = cls(
            id = id,
            codigo=codigo,
            nome=nome,
            status_vendedor=status,
            meta_vendedor=meta
        )
        db.session.add(novo_vendedor)
        try:
            db.session.commit()
            return True
        except Exception as e:
            print(f"Erro ao criar vendedor: {e}")
            db.session.rollback()
            return False
        
    @classmethod
    def delete(cls, id):
        vendedor = cls.query.get(id)
        if vendedor:
            db.session.delete(vendedor)
            db.session.commit()
            return True
        return False
 
def consultar_dados():
    data_atual = datetime.now()
    data_6_meses_atras = data_atual - timedelta(days=6*30)
    ano = data_6_meses_atras.year
    mes = data_6_meses_atras.month
    query_sice = f"""
        SELECT 
            vendedor,
            YEAR(data) as ano,
            MONTH(data) as mes,
            SUM(totalbruto) as totalbruto_mensal,
            SUM(total) as total_mensal,
            SUM(desconto) as desconto_mensal,
            SUM(devolucaovenda) as devolucaovenda_mensal,
            SUM(CASE WHEN tipopagamento = 'CA' THEN 1 ELSE 0 END) as ca_mensal,
            SUM(CASE WHEN tipopagamento = 'CH' THEN 1 ELSE 0 END) as ch_mensal,
            SUM(CASE WHEN tipopagamento = 'CR' THEN 1 ELSE 0 END) as cr_mensal,
            SUM(CASE WHEN tipopagamento = 'DH' THEN 1 ELSE 0 END) as dh_mensal,
            SUM(CASE WHEN tipopagamento = 'DV' THEN 1 ELSE 0 END) as dv_mensal,
            SUM(CASE WHEN tipopagamento = 'FI' THEN 1 ELSE 0 END) as fi_mensal,
            SUM(CASE WHEN tipopagamento = 'FN' THEN 1 ELSE 0 END) as fn_mensal,
            SUM(CASE WHEN tipopagamento = 'PD' THEN 1 ELSE 0 END) as pd_mensal,
            SUM(CASE WHEN tipopagamento = 'RN' THEN 1 ELSE 0 END) as rn_mensal,
            SUM(CASE WHEN tipopagamento = 'RV' THEN 1 ELSE 0 END) as rv_mensal,
            SUM(CASE WHEN tipopagamento = 'Se' THEN 1 ELSE 0 END) as se_mensal,
            COUNT(DISTINCT documento) as atendimentos_mensal
        FROM sice.contdocs
        WHERE YEAR(data) >= :ano AND MONTH(data) >= :mes
        GROUP BY vendedor, YEAR(data), MONTH(data);
    """
    
    Session = sessionmaker(bind=db.engine)
    session = Session()
    resultados_sice = session.execute(text(query_sice), {'ano': ano, 'mes': mes}).fetchall()
    session.close()
    
    return resultados_sice

def att_dados():
    vendas = consultar_dados()
    for v in vendas:
        if all(value is None for value in (v[0], v[1], v[2])):
            continue
        else:
            codigo = v[0] 
            if v[0] is not None and len(v[0]) == 2:
                codigo = '0'+v[0]
            nome = Vendedores_nordepy.get_nome_codigo(codigo) 
            ano = v[1]
            mes = v[2]
            totalbruto_mensal = v[3] if v[3] is not None else 0.0
            total_mensal = v[4] if v[4] is not None else 0.0
            desconto_mensal = v[5] if v[5] is not None else 0.0
            devolucaovenda_mensal = v[6] if v[6] is not None else 0.0
            ca_mensal = v[7] if v[7] is not None else 0.0
            ch_mensal = v[8] if v[8] is not None else 0.0
            cr_mensal = v[9] if v[9] is not None else 0.0
            dh_mensal = v[10] if v[10] is not None else 0.0
            dv_mensal = v[11] if v[11] is not None else 0.0
            fi_mensal = v[12] if v[12] is not None else 0.0
            fn_mensal = v[13] if v[13] is not None else 0.0
            pd_mensal = v[14] if v[14] is not None else 0.0
            rn_mensal = v[15] if v[15] is not None else 0.0
            rv_mensal = v[16] if v[16] is not None else 0.0
            se_mensal = v[17] if v[17] is not None else 0.0
            atendimentos_mensal = v[18] if v[18] is not None else 0.0
            Dados_vendas.update(ano = ano, mes= mes, vendedor= nome, totalbruto=totalbruto_mensal, 
                                desconto=desconto_mensal, total= total_mensal, devolucaovenda= devolucaovenda_mensal,
                                CA=ca_mensal, CH= ch_mensal, CR= cr_mensal, DH= dh_mensal, DV=dv_mensal, FI=fi_mensal, 
                                FN= fn_mensal, PD= pd_mensal, RN= rn_mensal, RV= rv_mensal, Se=se_mensal, atendimentos=atendimentos_mensal)

def obter_total_registros():
    query = """SELECT COUNT(*)
                FROM sice.contdocs
                WHERE YEAR(data) >= 2019;"""
    Session = sessionmaker(bind=db.engine)
    session = Session()
    total_registros = session.execute(text(query)).scalar()
    session.close()
    return total_registros

def consultar_todos_dados():
    query_sice = """
        SELECT 
            vendedor,
            YEAR(data) as ano,
            MONTH(data) as mes,
            SUM(totalbruto) as totalbruto_mensal,
            SUM(total) as total_mensal,
            SUM(desconto) as desconto_mensal,
            SUM(devolucaovenda) as devolucaovenda_mensal,
            SUM(CASE WHEN tipopagamento = 'CA' THEN 1 ELSE 0 END) as ca_mensal,
            SUM(CASE WHEN tipopagamento = 'CH' THEN 1 ELSE 0 END) as ch_mensal,
            SUM(CASE WHEN tipopagamento = 'CR' THEN 1 ELSE 0 END) as cr_mensal,
            SUM(CASE WHEN tipopagamento = 'DH' THEN 1 ELSE 0 END) as dh_mensal,
            SUM(CASE WHEN tipopagamento = 'DV' THEN 1 ELSE 0 END) as dv_mensal,
            SUM(CASE WHEN tipopagamento = 'FI' THEN 1 ELSE 0 END) as fi_mensal,
            SUM(CASE WHEN tipopagamento = 'FN' THEN 1 ELSE 0 END) as fn_mensal,
            SUM(CASE WHEN tipopagamento = 'PD' THEN 1 ELSE 0 END) as pd_mensal,
            SUM(CASE WHEN tipopagamento = 'RN' THEN 1 ELSE 0 END) as rn_mensal,
            SUM(CASE WHEN tipopagamento = 'RV' THEN 1 ELSE 0 END) as rv_mensal,
            SUM(CASE WHEN tipopagamento = 'Se' THEN 1 ELSE 0 END) as se_mensal,
            COUNT(DISTINCT documento) as atendimentos_mensal
        FROM sice.contdocs
        WHERE YEAR(data) >= 2019
        GROUP BY vendedor, YEAR(data), MONTH(data);
    """
    
    Session = sessionmaker(bind=db.engine)
    session = Session()
    resultados_sice = session.execute(text(query_sice)).fetchall()
    session.close()
    
    return resultados_sice

def att_todos_dados(): 
    vendas = consultar_todos_dados()
    for v in vendas:
        if all(value is None for value in (v[0], v[1], v[2])):
            continue
        else:
            codigo = v[0] 
            if v[0] is not None and len(v[0]) == 2:
                codigo = '0'+v[0]
            nome = Vendedores_nordepy.get_nome_codigo(codigo) 
            ano = v[1]
            mes = v[2]
            totalbruto_mensal = v[3] if v[3] is not None else 0.0
            total_mensal = v[4] if v[4] is not None else 0.0
            desconto_mensal = v[5] if v[5] is not None else 0.0
            devolucaovenda_mensal = v[6] if v[6] is not None else 0.0
            ca_mensal = v[7] if v[7] is not None else 0.0
            ch_mensal = v[8] if v[8] is not None else 0.0
            cr_mensal = v[9] if v[9] is not None else 0.0
            dh_mensal = v[10] if v[10] is not None else 0.0
            dv_mensal = v[11] if v[11] is not None else 0.0
            fi_mensal = v[12] if v[12] is not None else 0.0
            fn_mensal = v[13] if v[13] is not None else 0.0
            pd_mensal = v[14] if v[14] is not None else 0.0
            rn_mensal = v[15] if v[15] is not None else 0.0
            rv_mensal = v[16] if v[16] is not None else 0.0
            se_mensal = v[17] if v[17] is not None else 0.0
            atendimentos_mensal = v[18] if v[18] is not None else 0.0
            try:
                Dados_vendas.update(ano=ano, mes=mes, vendedor=nome, totalbruto=totalbruto_mensal, 
                                    desconto=desconto_mensal, total=total_mensal, devolucaovenda=devolucaovenda_mensal,
                                    CA=ca_mensal, CH=ch_mensal, CR=cr_mensal, DH=dh_mensal, DV=dv_mensal, FI=fi_mensal, 
                                    FN=fn_mensal, PD=pd_mensal, RN=rn_mensal, RV=rv_mensal, Se=se_mensal, atendimentos=atendimentos_mensal)

            except Exception as e:
                print(f"Erro durante o upload: {e}")
                return False
            
    return True
            
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    att_dados()
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loggando', methods=['POST'])
def loggando():
    if request.method == 'POST':
        nome = request.form.get('Nome')
        senha = request.form.get('Senha')
        user = User.query.filter_by(user=nome).first()

        if user and user.senha == senha:
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('painel'))
        else:
            flash('Usuário ou senha incorretos. Tente novamente.', 'error')
            return redirect(url_for('login'))

@app.route('/painel')
@login_required
def painel():
    att_dados()
    nome = current_user.user
    nivel = current_user.nivel
    return render_template('painel.html', nome_usuario=nome, nivel=nivel)

@app.route('/vendedores')
@login_required
def vendedores():
    nome_usuario = current_user.user
    nivel = current_user.nivel
    dados_vendedores = Vendedores_nordepy.query.all()
    return render_template('vendedores.html', nome_usuario=nome_usuario, dados=dados_vendedores, nivel = nivel)
                
@app.route('/mod_vendedores')
@login_required
def mod_vendedores():
    nome_usuario = current_user.user
    nivel = current_user.nivel
    dados_vendedores = Vendedores_nordepy.query.all()
    return render_template('mod_vendedores.html', nome_usuario=nome_usuario, dados=dados_vendedores, nivel = nivel)

@app.route('/atualizar_dados', methods=['POST'])
@login_required
def atualizar_dados():
    if request.method == 'POST':
        try:
            alteracoes_realizadas = False
            for vendedor_id in request.form.getlist('id[]'):
                id = int(vendedor_id)
                status = bool(int(request.form.get(f'status[{id}]', 0)))
                nova_meta_input = request.form.get(f'nova_meta[{id}]', '')            
                try:
                    meta = float(nova_meta_input.replace(',', '.'))
                except ValueError:
                    meta = 0.00
                    
                if Vendedores_nordepy.update_status_meta(id, status, meta):
                    alteracoes_realizadas = True

            if alteracoes_realizadas:
                    flash("Dados alterados com sucesso!", 'success')
            else:
                    flash("Nenhuma alteração realizada.", 'info')
                    
            return redirect('/vendedores')

        except Exception as e:
            flash("Erro ao atualizar os dados. Por favor, tente novamente.", 'error')
            return redirect('/vendedores')

shared_data = {'all_data': pd.DataFrame()}
def update_shared_data():
    dados_pd = Dados_vendas.get_all()
    shared_data['all_data'] = dados_pd
 
with app.app_context():
    update_shared_data()
       
cockpit_dash = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/')
cockpit_dash.layout = html.Div(children=[
    dcc.RadioItems(
        id='ano-radio',
        options= [{'label': str(year), 'value': year} for year in shared_data['all_data']['ano'].unique()],
        value= None,
        inline=True
    ),
    dcc.RadioItems(
        id='mes-radio',
        options=[{'label': 'Todos os Meses', 'value': 'all'}] +
                [{'label': str(month), 'value': month} for month in shared_data['all_data']['mes'].unique()],
        value= None,
        inline=True
    ),
    dcc.Dropdown(
        id='vendedor-dropdown',
        options=[{'label': 'Todos os Vendedores', 'value': 'all'}] +
                [{'label': vendedor, 'value': vendedor} for vendedor in shared_data['all_data']['vendedor'].unique()],
        value=['all'], 
        multi=True 
    ),
    dcc.Graph(
        id='subplot-1',
        className='subplot',
    ),
    dcc.Graph(
        id='subplot-2',
        className='subplot',
    ),
    dcc.Graph(
        id='subplot-3',
        className='subplot',
    ),
])

@app.route('/cockpit')
@login_required
def cockpit():
    att_dados()
    update_shared_data()
    nome = current_user.user
    nivel = current_user.nivel
    return render_template('cockpit.html', nome_usuario=nome, nivel=nivel)

@cockpit_dash.callback(
    [Output('ano-radio', 'options'),
     Output('ano-radio', 'value')],
    [Input('ano-radio', 'value')],
    [State('ano-radio', 'value')]
)
def update_ano_dropdown(selected_ano, current_value):
    update_shared_data()
    if 'all_data' in shared_data and 'ano' in shared_data['all_data'].columns:
        options = shared_data['all_data']['ano'].unique()
    else:
        options = []
    options = [{'label': str(year), 'value': year} for year in options]
    value = selected_ano if selected_ano in options else options[0]['value']
    value = current_value
    
    return options, value

@cockpit_dash.callback(
    Output('mes-radio', 'options'),
    Output('mes-radio', 'value'),
    [Input('ano-radio', 'value')]
)
def update_mes_dropdown(selected_ano):
    update_shared_data()
    if 'all_data' in shared_data and 'ano' in shared_data['all_data'].columns and 'mes' in shared_data['all_data'].columns:
        options = shared_data['all_data'][shared_data['all_data']['ano'] == selected_ano]['mes'].unique()
    else:
        options = []

    all_months_option = {'label': 'Todos os Meses', 'value': None}
    options = [all_months_option] + [{'label': str(month), 'value': month} for month in options]
    value = options[0]['value'] if not selected_ano else None

    return options, value

@cockpit_dash.callback(
    [   Output('subplot-1', 'figure'),
        Output('subplot-2', 'figure'),
        Output('subplot-3', 'figure'),
    ],
    [Input('ano-radio', 'value'),
     Input('mes-radio', 'value'),
     Input('vendedor-dropdown', 'value')]
)
def update_graph(selected_ano, selected_mes, selected_vendedor):
    filtered_data = shared_data['all_data'].copy() 
    title_suffix = ''
    if selected_vendedor != ['all'] and selected_vendedor != [] :
        if not isinstance(selected_vendedor, list):
            selected_vendedores = [selected_vendedor]
        else:
            selected_vendedores = selected_vendedor

        if selected_ano is not None:
            filtered_data = shared_data['all_data'][shared_data['all_data']['ano'] == selected_ano]
            title_suffix = selected_ano
     
        figure = {
            'data': [],
            'layout': {
                'title': f'Saldo ao Longo dos Meses - {title_suffix}',
                'xaxis': {'title': 'Meses'},
                'yaxis': {'title': 'Saldo'},
                'height': 350,
                'margin': {'l': 150, 'r': 50, 't': 50, 'b': 50},
                'row': 1,}}
        
        figure2 = {
            'data': [],
            'layout': {
                'title': f'Ticket Médio ao Longo dos Meses - {title_suffix}',
                'xaxis': {'title': 'Meses'},
                'yaxis': {'title': 'Ticket Médio'},
                'height': 350,
                'margin': {'l': 150, 'r': 50, 't': 50, 'b': 50},
                'row': 2,}}
        
        figure3 = {
            'data': [],
            'layout': {
                'title': f'Atendimentos ao Longo dos Meses - {title_suffix}',
                'xaxis': {'title': 'Meses'},
                'yaxis': {'title': 'Atendimentos'},
                'height': 350,
                'margin': {'l': 150, 'r': 50, 't': 50, 'b': 50},
                'row': 3,}}

        for i, vendedor in enumerate(selected_vendedores):
            vendedor_data = filtered_data[filtered_data['vendedor'] == vendedor]
            vendedor_data.loc[:, 'saldo'] = vendedor_data['total'] - vendedor_data['devolucaovenda']           
            trace = {
                'x': ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
                'y': vendedor_data['saldo'], 
                'type': 'bar', 
                'name': vendedor,
                'text': [format_currency(valor, 'BRL', locale='pt_BR') for valor in vendedor_data['saldo']],
                'textposition': 'inside',
                'textfont': {'color': 'white' if sum([i * 50, i * 30, i * 20]) > 255 * 1.5 else 'white'},
                'marker': {'color': f'rgba({i * 50}, {i * 30}, {i * 20}, 0.8)'},
            }
            figure['data'].append(trace)
            
            vendedor_data['ticket']= (vendedor_data['total'] - vendedor_data['devolucaovenda']) / vendedor_data['atendimentos']
            vendedor_data['ticket'] = vendedor_data['ticket'].astype(float)
            trace_ticket = {
                'x': ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
                'y': vendedor_data['ticket'].tolist(), 
                'type': 'bar', 
                'name': f'{vendedor} - Ticket Médio',
                'text': [[round(float(valor), 2) for valor in vendedor_data['ticket']]],
                'textposition': 'inside',
                'textfont': {'color': 'white' if sum([i * 50, i * 30, i * 20]) > 255 * 1.5 else 'white'},
                'marker': {'color': f'rgba({i * 50}, {i * 30}, {i * 20}, 0.8)'},
            }
            figure2['data'].append(trace_ticket)

            trace_atendimentos = {
                'x': ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
                'y': vendedor_data['atendimentos'], 
                'type': 'bar',
                'name': vendedor,
                'text': [round(valor, 0) for valor in vendedor_data['atendimentos']],
                'textposition': 'inside',
                'textfont': {'color': 'white' if sum([i * 50, i * 30, i * 20]) > 255 * 1.5 else 'white'},
                'marker': {'color': f'rgba({i * 50}, {i * 30}, {i * 20}, 0.8)'},
            }
            figure3['data'].append(trace_atendimentos)
            
            media_atendimentos = vendedor_data['atendimentos'].mean()
            trace_media_atendimentos = {
                'x': ['Janeiro', 'Dezembro'],
                'y': [media_atendimentos, media_atendimentos],
                'type': 'scatter',
                'mode': 'lines',
                'name': f'{vendedor} - Média de Atendimentos',
                'line': {'dash': 'dash'},
                'text': [f'Média: {media_atendimentos}', ''],
            }
            figure3['data'].append(trace_media_atendimentos)
        return figure, figure2, figure3

    else:
        if selected_ano is None:
            filtered_data = shared_data['all_data'].copy()
            title_suffix = 'Todos os Anos'
            print('foi 3')
        else:
            if selected_mes is None:
                filtered_data = shared_data['all_data'][shared_data['all_data']['ano'] == selected_ano]
                filtered_data['saldo'] = filtered_data['total'] - filtered_data['devolucaovenda']
                filtered_data['ticket'] = (filtered_data['total'] - filtered_data['devolucaovenda']) / filtered_data['atendimentos']
                filtered_data = filtered_data[filtered_data['vendedor'].apply(lambda x: len(str(x)) >= 4 if isinstance(x, (str, int)) else False)]
                filtered_data = filtered_data.sort_values(by='saldo', ascending=True)
                filtered_data = filtered_data.sort_values(by='ticket', ascending=True)
                grouped_data = filtered_data.groupby('vendedor')['saldo'].sum().reset_index()
                grouped_data_2 = filtered_data.groupby('vendedor')['ticket'].sum().reset_index()
                grouped_data_3 = filtered_data.groupby('vendedor')['atendimentos'].sum().reset_index()
                title_suffix = f'Todo o Ano - {selected_ano}'
            else:
                filtered_data = shared_data['all_data'][
                    (shared_data['all_data']['ano'] == selected_ano) 
                    & (shared_data['all_data']['mes'] == selected_mes)
                ]
                title_suffix = f'{selected_mes}/{selected_ano}'
                filtered_data['saldo'] = filtered_data['total'] - filtered_data['devolucaovenda']
                filtered_data['ticket'] = (filtered_data['total'] - filtered_data['devolucaovenda']) / filtered_data['atendimentos']
                filtered_data = filtered_data[filtered_data['vendedor'].apply(lambda x: len(str(x)) >= 4 if isinstance(x, (str, int)) else False)]
                filtered_data = filtered_data.sort_values(by='saldo', ascending=True)
                filtered_data2 = filtered_data.sort_values(by='ticket', ascending=True)
                grouped_data = filtered_data[['saldo', 'vendedor']]
                grouped_data_2 = filtered_data2.groupby('vendedor')['ticket'].sum().reset_index()
                grouped_data_3 = filtered_data.groupby('vendedor')['atendimentos'].sum().reset_index()
   
        figure4 = {
            'data': [{
                'x': grouped_data['saldo'], 
                'y': grouped_data['vendedor'], 
                'type': 'bar', 
                'name': 'Saldo', 
                'orientation': 'h',
                'text': [format_currency(valor, 'BRL', locale='pt_BR') for valor in grouped_data['saldo']],
                'textposition': 'inside',
            }],
            'layout': {
                'title': f'Total por Vendedor - {title_suffix}',
                'xaxis': {'title': ''},
                'yaxis': {'title': ''},
                'height': 400,
                'margin': {'l': 150, 'r': 50, 't': 50, 'b': 50},
                'row': 1,
            }
        }
        
        figure5 = {
            'data': [{
                'x': grouped_data_2['ticket'],
                'y': grouped_data_2['vendedor'], 
                'type': 'bar', 
                'name': 'Ticket Médio', 
                'orientation': 'h',
                'text': [round(valor, 2) for valor in grouped_data_2['ticket']],
                'textposition': 'inside',}],
            'layout': {
                'title': f'Ticket Médio por Vendedor - {title_suffix}',
                'xaxis': {'title': ''},
                'yaxis': {'title': ''},
                'height': 400,
                'margin': {'l': 150, 'r': 50, 't': 50, 'b': 50},
                'row': 2,}}
        
        figure6 = {
            'data': [ {
                'x': grouped_data_3['atendimentos'],
                'y': grouped_data_3['vendedor'],
                'type': 'bar',
                'name': 'Atendimentos',
                'orientation': 'h',
                'text': [round(valor, 0) for valor in grouped_data_3['atendimentos']],
                'textposition': 'inside'},
                {
                'x': [grouped_data_3['atendimentos'].mean()]*10,
                'y': [grouped_data_3['vendedor'].min(), grouped_data_3['vendedor'].max()],
                'type': 'line',
                'mode': 'lines',
                'name': 'Média',
                'line': {'solid': 'solid', 'color': 'red', 'width': 3}} ],
            'layout': {
                'title': f'Atendimentos por Vendedor - {title_suffix}',
                'xaxis': {'title': ''},
                'yaxis': {'title': ''},
                'height': 400,
                'margin': {'l': 150, 'r': 50, 't': 50, 'b': 50},
                'row': 3,}}
        
        return figure4, figure5, figure6
        
@app.route('/opcoes')
@login_required
def opcoes():
    nivel = current_user.nivel
    nome = current_user.user
    return render_template('opcoes.html', nome_usuario=nome, nivel = nivel)

@app.route('/opcoes_att')
@login_required
def opcoes_att():
    try:
        alteracoes_realizadas = False
        total_registros = obter_total_registros()  
        registros_processados = 0

        for _ in consultar_todos_dados():
            registros_processados += 1
            progress = float((registros_processados / total_registros) * 100)
            flash_js = f"updateProgressBar({progress});"
            flash_js += "showChartContainer();"
            flash_js += "if(window.flashProgressBar) { window.flashProgressBar(); }"
            flash(flash_js, "js")

        if alteracoes_realizadas:
            flash("Dados atualizados com sucesso!", 'success')
        else:
            flash("Alguns dados não foram atualizados.", 'info')

        return redirect('/opcoes')

    except Exception as e:
        flash(str(e), 'error')
        return redirect('/opcoes')
 
@app.route('/fazer_previsao')
@login_required
def fazer_previsao():
    nivel = current_user.nivel
    nome = current_user.user
    dados = Dados_vendas.dados_ia()
    dados = dados.sort_values(by=['ano', 'mes'])
    dados_agrupados = dados.groupby(['ano', 'mes']).sum().reset_index()
    loaded_model = tf.keras.models.load_model("modelo_treinado.h5")
    X_test = dados_agrupados.iloc[-5:, :]
    previsoes = loaded_model.predict(X_test)
    dados_previsao_plot = pd.DataFrame({
        'data': [f"{ano}-{mes}" for ano, mes in zip(dados_agrupados['ano'].iloc[-5:], dados_agrupados['mes'].iloc[-5:])],
        'previsao': previsoes.squeeze() /10
    })
    fig = go.Figure([go.Bar( x= dados_previsao_plot['data'], y=dados_previsao_plot['previsao'], name='Previsão'), 
          go.Scatter(x=dados_previsao_plot['data'], y=dados['total'], mode='lines', name='Real')])
    fig.update_layout(
        xaxis_title='Data (Ano-Mês)',
        yaxis_title='Valor (R$)',
    )

    return render_template('previsao.html', graph=fig.to_html(full_html=False), nome_usuario=nome, nivel=nivel)
   
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dash')
def dash():
    def create_dash_layout():
        primeiro_dia_mes_atual = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ativos = Vendedores_nordepy.query.filter_by(status_vendedor=True).filter(Vendedores_nordepy.nome != 'LOJA').all()
        ano_atual = primeiro_dia_mes_atual.year
        mes_atual = primeiro_dia_mes_atual.month
        dados_df = Contdocs_sice.obter_dados_por_ano_mes(ano= ano_atual, mes=mes_atual)
        totais_vendas = {}
        for vendedor in ativos:
            total_vendas_por_vendedor = dados_df.groupby('vendedor')['total'].sum()
            total_vendas_por_vendedor = dados_df.groupby('vendedor')['total'].sum().reset_index()
            total_vendas_por_vendedor['vendedor'] = total_vendas_por_vendedor['vendedor'].apply(Vendedores_nordepy.get_nome_codigo(vendedor.codigo))
            totais_vendas[(vendedor.nome, vendedor.codigo)] = total_vendas_por_vendedor.set_index('vendedor')['total'].to_dict()
        
        #Loja
        soma_total_vendas = dados_df['total'].sum()
        meta_loja = Vendedores_nordepy.query.filter_by(nome='LOJA').first().meta_vendedor
        percentual_meta_loja = (soma_total_vendas / meta_loja) * 100 if meta_loja != 0 else 0

        # Rank
        percentuais_vendedores = {}
        for nome_codigo, total_vendas in totais_vendas.items():
            nome, codigo = nome_codigo
            total_vendas = total_vendas.get(nome, 0)
            meta_vendedor = Vendedores_nordepy.get_meta_codigo(codigo=codigo)
            percentual_meta_vendedor = (total_vendas / meta_vendedor) * 100 if meta_vendedor != 0 else 0
            percentuais_vendedores[nome] = percentual_meta_vendedor

        df_percentuais_vendedores = pd.DataFrame(list(percentuais_vendedores.items()), columns=['Nome', 'Percentual'])
        df_percentuais_vendedores['Percentual'] *= 100
        df_top_5_vendedores = df_percentuais_vendedores.nlargest(5, 'Percentual')
        nomes_vendedores = df_top_5_vendedores['Nome'].tolist()
        percentuais_top_5 = df_top_5_vendedores['Percentual'].tolist()
        percentual = [x for x in percentuais_top_5]
        
        fig = px.bar(
            x= percentual,
            y= nomes_vendedores,
            orientation='h',
            labels={'x': '', 'y': ''},
            title='Top 5 Vendedores',
        )

        fig.update_layout(
            plot_bgcolor='#9B9B9B',
            title={'text': 'Top 5 Vendedores', 'x': 0.5, 'xanchor': 'center'},
            xaxis=dict(range=[0, 110], zeroline=False, autorange=False, dtick=150, showticklabels=False),
            yaxis=dict(autorange=True),
            margin=dict(l=0, r=0, t=40, b=0),
            autosize=False
        )

        fig.update_traces(
            marker_color='#F38432',
            texttemplate='%{text:.2%}',
            text=[x / 100 for x in percentual],
            textposition='inside',
            textfont=dict(size=10, color='black'),
        )

        fig2 = px.bar(
            x=[percentual_meta_loja],
            y=[''],
            orientation='h',
            labels={'x': '', 'y': ''},
            title='Meta do Mês',
        )

        fig2.update_layout(
            plot_bgcolor='#9B9B9B',
            title={'text': 'Meta do Mês', 'x': 0.5, 'xanchor': 'center'},
            xaxis=dict(range=[0, 110], zeroline=False, autorange=False, dtick=150, showticklabels=False),
            yaxis=dict(autorange=True, fixedrange=True, range=[-0.1, 0.1]),
            margin=dict(l=0, r=0, t=50, b=0),
            template='plotly', 
            autosize=False,
            height=100,
        )

        fig2.update_traces(
            marker_color='#F38432',
            texttemplate='%{text:.2%}',
            text=[percentual_meta_loja / 100],
            textposition='inside',
            textfont=dict(size=10, color='black'),
        )
        
        return fig, fig2
    fig, fig2 = create_dash_layout()
    return render_template('dash.html', dash_graph=fig.to_html(full_html=False), dash_graph2=fig2.to_html(full_html=False))

if __name__ == '__main__':
    app.run(debug=False, port= 5000)