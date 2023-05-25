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
        self

    def popup_mostrar_artigo_produto(self):
        self.open()
        for nome in produtos_list_event:
            if nome['nome'].lower().find(self.input_nome) >= 0:
                produto = {'codigo':nome['codigo'], 'nome':nome['nome'], 'preco':nome['preco'], 'quantidade':nome['quantidade']}
                self.ids.rvs.add_artigo(produto)
    
    def selecionar_art_produto(self):
        indice = self.ids.rvs.add_artigo()
        if indice >= 0:
            _art_produto = self.ids.rvs.data[indice]
            artigo = {}
            artigo['codigo'] = _art_produto['codigo']
            artigo['nome'] = _art_produto['nome']
            artigo['preco'] = _art_produto['preco']
            artigo['quantidade_carrinho'] = 1
            artigo['quantidade_invent'] = _art_produto['quantidade']
            artigo['preco_total'] = _art_produto['preco']
            
    
    
class VendasJanela(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total = 0.0

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

    def deletar_produto(self):
        print("DELETAR PRODUTO FUNCIONANDO")

    def trocar_produto(self):
        print("TROCAR PRODUTO ESTA FUNCIONANDO")

    def pagar(self):
        print("pagar")

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
