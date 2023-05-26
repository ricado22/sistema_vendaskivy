from kivy.app import App 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup

produtos_list_event = [
	{'codigo': '100', 'nome': 'LEITE 1L', 'preco': 20.0, 'quantidade': 20},
	{'codigo': '101', 'nome': 'CERIAL 500g', 'preco': 50.5, 'quantidade': 15}, 
	{'codigo': '102', 'nome': 'SABONETES', 'preco': 25.0, 'quantidade': 10},
	{'codigo': '103', 'nome': 'COCA COLA 2L', 'preco': 80.0, 'quantidade': 20},
	{'codigo': '104', 'nome': 'ARROZ 20kg', 'preco': 750.0, 'quantidade': 5},
	{'codigo': '105', 'nome': 'CREME', 'preco': 100.0, 'quantidade': 25},
	{'codigo': '106', 'nome': 'PAPEL TOALHA 4 ROLOS', 'preco': 35.5, 'quantidade': 30},
	{'codigo': '107', 'nome': 'SABAO', 'preco': 65.0, 'quantidade': 5},
	{'codigo': '108', 'nome': 'GUARANA 600ml', 'preco': 15.0, 'quantidade': 10}
]

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    touch_deselect_last = BooleanProperty(True)




class SelectableBoxLayout(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_has_cod'].text = str(1+index)
        self.ids['_artigo_produto'].text = data['nome'].capitalize()
        self.ids['_quantidade'].text = str(data['quantidade_carrinho'])
        self.ids['_preco_por_produto'].text = str("{:.2f}".format(data['preco']))
        self.ids['_preco'].text = str("{:.2f}".format(data['preco_total']))
        return super(SelectableBoxLayout, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayout, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.data[index]['selecionado']=True
        else:
            rv.data[index]['selecionado']=False

##########################################################################################

class SelectableBoxLayout_Popup(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_codigo'].text = data['codigo']
        self.ids['_artigo_produto'].text = data['nome'].capitalize()
        self.ids['_quantidade'].text = str(data['quantidade'])
        self.ids['_preco'].text = str("{:.2f}".format(data['preco']))
        
        return super(SelectableBoxLayout_Popup, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayout_Popup, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.data[index]['selecionado']=True
        else:
            rv.data[index]['selecionado']=False

###############################################################################################

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []
        self.trocar_produto=None
            

    def add_artigo(self, artigo):
        artigo['selecionado'] = False
        indice = -1
        if self.data:
            for i in range(len(self.data)):
                if artigo['codigo'] == self.data[i]['codigo']:
                    indice = i
            if indice >= 0:
                self.data[indice]['quantidade_carrinho'] += 1
                self.data[indice]['preco_total'] = self.data[indice]['preco'] * self.data[indice]['quantidade_carrinho']
                self.refresh_from_data()
            else:
                self.data.append(artigo)
        else:
            self.data.append(artigo)

    def deletar_art_produto(self):
        indice = self.art_selecionado_produto()
        preco = 0
        if indice >= 0:
            self._layout_manager.deselect_node(self._layout_manager._last_selected_node)
            preco = self.data[indice]['preco_total']
            self.data.pop(indice)
            self.refresh_from_data()
        return preco
    
    def mod_trocar_arte(self):
        indice = self.art_selecionado_produto()
        if indice >= 0:
            popup = Trocar_Qtde_Popup(self.data[indice], self.atualizar_art_qtide)
            popup.open()

    def atualizar_art_qtide(self, valor):
        indice = self.art_selecionado_produto()
        if indice >= 0:
            if valor==0:
                self.data.pop(indice)
                self._layout_manager.deselect_node(self._layout_manager._last_selected_node)
            else:
                self.data[indice]['quantidade_carrinho'] = valor
                self.data[indice]['preco_total'] = self.data[indice]['preco']*valor
            
            self.refresh_from_data()
            novo_total = 0
            for data in self.data:
                novo_total += data['preco_total']
                self.trocar_produto(False, novo_total)

    def art_selecionado_produto(self):
        indice=-1
        for i in range(len(self.data)):
            if self.data[i]['selecionado']:
                indice=i
            break
        return indice

class Produto_Nome_Popup(Popup):
    def __init__(self, input_nome, add_produto_callback, **kwargs):
        super(Produto_Nome_Popup, self).__init__(**kwargs)
        self.input_nome = input_nome
        self.add_produto = add_produto_callback
    
    def popup_mostrar_artigo_produto(self):
        self.open()
        for nome in produtos_list_event:
            if nome['nome'].lower().find(self.input_nome) >= 0:
                produto = {'codigo':nome['codigo'], 'nome':nome['nome'], 'preco':nome['preco'], 'quantidade':nome['quantidade']}
                self.ids.rvs.add_artigo(produto)

    def selecionar_art_produto(self):
        indice = self.ids.rvs.art_selecionado_produto()
        if indice >= 0:
            _art_produto = self.ids.rvs.data[indice]
            artigo = {}
            artigo['codigo'] = _art_produto['codigo']
            artigo['nome'] = _art_produto['nome']
            artigo['preco'] = _art_produto['preco']
            artigo['quantidade_carrinho'] = 1
            artigo['quantidade_invent'] = _art_produto['quantidade']
            artigo['preco_total'] = _art_produto['preco']
            if callable(self.add_produto):           
                self.add_produto(artigo)
            self.dismiss()

class Trocar_Qtde_Popup(Popup):
    def __init__(self, data, atualizar_art_qtide_callback, **kwargs):
        super(Trocar_Qtde_Popup, self).__init__(**kwargs)
        self.data = data
        self.atualizar_art_qtide = atualizar_art_qtide_callback
        self.ids.nova_qtide_1.text = "produto:"+ self.data['nome'].capitalize()
        self.ids.nova_qtide_2.text = "Quantidade:"+ str(self.data['quantidade_carrinho'])

    def validar_text_input(self, texto_input):
        try:
            nova_qtide = int(texto_input)
            self.ids.notificacao_nao_valida.text = ''
            self.atualizar_art_qtide(nova_qtide)
            self.dismiss()
        except:
            self.ids.notificacao_nao_valida.text = 'Esta quantidade não esta valida'
    
class PagarPopup(Popup):
    def __init__(self, total, terminar_pagamento_callback, **kwargs):
        super(PagarPopup, self).__init__(**kwargs)
        self.total = total
        self.terminar_pagamento = terminar_pagamento_callback
        self.ids.total.text = 'R$ ' + "{:.2f}".format(self.total)
        self.ids.botao_pagar.bind(on_release=self.dismiss)
    
    def mostrar_troca(self):
        recebido = self.ids.recebido.text
        try:
            troco = float(recebido)-float(self.total)
            if troco >= 0:
                self.ids.troco.text = 'R$ ' + "{:.2f}".format(troco)
                self.ids.botao_pagar.disabled = False
            else:
                self.ids.troco.text = 'valor abaixo a ser pago'
        except:
            self.ids.troco.text = 'Valor incorreto'

class VendasJanela(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total = 0.0
        self.ids.rvs.trocar_produto = self.trocar_produto


    def add_produto_codigo(self, codigo):
        for produto in produtos_list_event:
            if codigo == produto['codigo']:
                artigo = {}
                artigo['codigo'] = produto['codigo']
                artigo['nome'] = produto['nome']
                artigo['preco'] = produto['preco']
                artigo['quantidade_carrinho'] = 1
                artigo['quantidade_invent'] = produto['quantidade']
                artigo['preco_total'] = produto['preco']
                self.add_produto(artigo)
                self.ids.pesquisar_codigo.text = ''
                break

    def add_produto_nome(self, nome):
        self.ids.pesquisar_nome.text=''
        pesq_nome_popup = Produto_Nome_Popup(nome, self.add_produto)
        pesq_nome_popup.popup_mostrar_artigo_produto()

    def add_produto(self, artigo):
        self.total += artigo['preco']
        self.ids.sub_total.text = 'R$ ' + "{:.2f}".format(self.total)
        self.ids.rvs.add_artigo(artigo)

    def deletar_art_produto(self):
        menor_preco = self.ids.rvs.deletar_art_produto()
        self.total -= menor_preco
        self.ids.sub_total.text = 'R$ ' + "{:.2f}".format(self.total)

    def trocar_produto(self, trocar=True, novo_total=None):
        if trocar:
            self.ids.rvs.mod_trocar_arte()
        else:
            self.total = novo_total
            self.ids.sub_total.text = 'R$ ' + "{:.2f}".format(self.total)

    def pagar(self):
        if self.ids.rvs.data:
            popup = PagarPopup(self.total, self.terminar_pagamento)
            popup.open()
        else:
            self.ids.notificacao_erro.text = 'Não tem nenhum produto a pagar'

    def terminar_pagamento(self):
        self.ids.notificacao_sucesso.text = 'Pagamento realizado com sucesso'

    def nova_compra(self):
        print("NOVA COMPRA ESTA FUNCIONANDO")

    def admin(self):
        print("Admin ESTA FUNCIONANDO")

    def signout(self):
        print("Signout ESTA FUNCIONANDO")


class VendasApp(App):
    def build(self):
        return VendasJanela()


if __name__ == '__main__':
    VendasApp().run()
