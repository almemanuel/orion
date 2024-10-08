import fire
from matplotlib import pyplot as plt
import numpy as np
from proptools import solid
from proptools import nozzle
from scipy.optimize import fsolve
from scipy.integrate import cumtrapz
# Ignorar o warning
import warnings
warnings.filterwarnings('ignore', 'The iteration is not making good progress')

# Tratamento de Erros
def imprimir(num, msg):
    """
    Imprimi uma mensagem na tela, dependendo da situação

    Parametros:
    num (str) -> valor que deveria ser numérico.
    Caso seja uma string vazia, significa que é um valor que não foi informado
    msg (str) -> contexto do parametro num

    Retorna:
    teste(num, msg), onde:
        str: num -> valor a ser testado em teste
        str: msg -> contexto de num
    """
    if num == '':
        num = input(f'Informe um valor para {msg}: ')
    else:
        num = input(f'Valor invalido para {msg}. Tente novamente: ')
    return teste(num, msg)


def teste(num, msg):
    """
    Testa se o parametro num é positivo

    Parametros:
    num (str) -> valor a ser testado.
    msg (str) -> contexto do parametro num

    Retorna:
    float(num), onde:
        str: num -> transformado em float, entrada válida
    imprimir(num, msg), onde:
        str: num -> valor invalido que deverá ser informado novamente pelo usuário
        str: msg -> contexto do parametro num
    """
    try:
        float(num) > 0
        return float(num)
    except:
        pass
    return imprimir(num, msg)


# Funções Essenciais
def TaxaExpansao(p_c, p_e, g):
    """
    Expressão da taxa de expansão em função da pressão de saída (Pe).
    Refer: Rocket Propulsion Elements, 8th Edition, Equation 3-25

    Parametros:
    p_c (float) -> Pressão da câmara [unidade: pascal].
    p_e (float) -> Pressão da saída do bucal [unidade: pascal].
    g (float) -> Razão da capacidade de calor de exaustão [unidade: adimensional].

    Retorna:
        float: AeAT -> Taxa de expansão (A_e / A_t) [unidade: adimensional]
    """
    AtAe = ((g + 1) / 2)**(1 / (g - 1)) \
        * (p_e / p_c)**(1 / g) \
        * ((g + 1) / (g - 1)*( 1 - (p_e / p_c)**((g -1) / g)))**0.5
    AeAt = 1/AtAe
    return AeAt

def RazaoPressoes(AeAt, g):
    """
    Determina a razão entre a pressão de saída e a pressão na câmara (Pe/Pc) a partir da taxa de expansão (Ae/At).
    Referência: Rocket Propulsion Elements, 8th Edition, Equation 3-25

    Parametros:
    AeAt (float) -> Taxa de expansão (A_e / A_t) [unidade: adimensional].
    g (float) -> Razão da capacidade de calor de exaustão [unidade: adimensional].

    Retorna:
    float: PePc -> Razão das pressões (Pe/Pc) [unidade: adimensional].
    """
    PePc = fsolve(lambda x: AeAt - TaxaExpansao(1., x, g), x0=1e-3 / AeAt)[0]
    assert PePc < 1
    return PePc


def coef_empuxo(p_c, p_e, g, p_a=None, er=None):
    """
    Coeficiente de Empuxo (Cf) | Referência: Equation 1-33a in Huzel and Huang.

    Parametros:
    p_c (float) -> Pressão na câmara [unidade: pascal].
    p_e (float) -> Pressão na saída do bucal [unidade: pascal].
    g (float) -> Razão da capacidade de calor de exaustão [unidade: adimensional].
    p_a (float) -> Pressão ambiente [unidade: pascal].
    AeAt (float) -> Taxa de expansão (A_e / A_t) [unidade: adimensional].

    Retorna:
    float: C_F -> Coeficiente de Empuxo
    """
    if (p_a is None and er is not None) or (er is None and p_a is not None):
        raise ValueError('Both p_a and er must be provided.')
    C_F = (2 * g**2 / (g - 1) \
        * (2 / (g + 1))**((g + 1) / (g - 1)) \
        * (1 - (p_e / p_c)**((g - 1) / g))
          )**0.5
    if p_a is not None and er is not None:
        C_F += er * (p_e - p_a) / p_c
    return C_F


def graphic(t, p_c, F):
    """
    Plota os resultados

    Parametros:
    t (float) -> tempo (segundo)
    p_c (float) -> pressao na camara (Pascal)
    F (float) -> força de empuxo (Newton)

    Retorna:
    def: plt.show() -> gráfico montado
    """
    ax1 = plt.subplot(2, 1, 1)
    plt.plot(t, p_c * 1e-6)
    plt.ylabel('Pressao na camara [MPa]')

    ax2 = plt.subplot(2, 1, 2)
    plt.plot(t, F * 1e-3)
    plt.ylabel('Impulso (nível do mar) [kN]')
    plt.xlabel('Tempo [s]')
    plt.setp(ax1.get_xticklabels(), visible=False)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0)
    return plt.show()


## main
def empuxo(gamma = '', m_molar = '', T_c = '', rho = '', n = '', r_in = '', r_ex = '', L = '', D_t = '', A_e = ''):
    """
    Insercao e validacao de dados e calculos |
    Os valores poderão ser informados antes da execução, seguindo o padrao --var value |
    Exemplo: python empuxo.py --r_in .2 --r_ex '' |
    Os valores serão testados e, ao final, um gráfico deve ser exibido

    Parametros:
    (str) gamma -> razão da capacidade de calor de exaustao
    (str) m_molar -> massa molar dos gases de escape (kg moleˆ-1)
    (str) T_c -> temperatura do combustivel (K)
    (str) rho -> densidade do combustivel solido (kg mˆ-3)
    (str) n -> expoente da taxa de queima do combustivel
    (str) r_in -> raio interno do grao (m)
    (str) r_ex -> raio externo do grao (m)
    (str) L -> comprimento do grao (m)
    (str) D_t -> diametro da garganta (m)
    (str) A_e -> area de saida da garganta (mˆ2)

    Retorno:
    def: graphic(t, p_c, F), onde:
        (float) t -> tempo (segundos)
        (float) p_c -> pressao na camara (Pascal)
        (float) F -> força de empuxoq
        (Newton)
    """

    # Propriedades do Combustível e do Gás de Exaustão
    gamma = teste(gamma, 'razão da capacidade de calor de exaustão')
    m_molar = teste(m_molar, 'massa molar dos gases de escape (kg moleˆ-1)')
    T_c = teste(T_c, 'temperatura do combustível (K)')
    rho = teste(rho, 'densidade do combustível sólido (kg mˆ-3)')
    n = teste(n, 'expoente da taxa de queima do combustível')
    a = 3.19e-3 * (8.260e6)**(-n) # Coeficiente da taxa de queima, sendo que o combustível queima a 3.19 mm s**-1 a 8.260 MPa [unidade: metro segundo**-1 pascal**-n].

    ### Geometria do Grão (cilíndrico com porte circular)
    r_in = teste(r_in, 'raio interno (m)')
    r_ex = teste(r_ex, 'raio externo (m)')
    L = teste(L, 'comprimento (m)')

    ### Geometria do Bucal
    D_t = teste(D_t, 'diametro da garganta (m)')
    A_e = teste(A_e, 'area de saida da garganta (mˆ2)')
    A_t = np.pi*((D_t)**2) # Área da garganta [unidade: metro**2]

    x = np.linspace(0, r_ex - r_in) # Distância em relação ao menor raio em direção ao maior raio, dividido em 50 segmentos [unidade: metro].
    A_b = 2 * np.pi * (r_in + x) * L # Área do combustivel sendo queimada por segmento [unidade: metro**2].
    K = A_b / A_t     # Razão da Área de Combustão (A_b) e Área da garganta (A_t)

    c = nozzle.c_star(gamma, m_molar, T_c) # Velocidade característica (c*)

    p_c = solid.chamber_pressure(A_b / A_t, a, n, rho, c) # pressão na camara em pascal

    r = a * p_c**n # taxa de queima

    p_e = p_c * RazaoPressoes(A_e / A_t, gamma) # pressao de saida em pascal

    p_a = 101325    # Pressão do ambiente [unidade: pascal]
    F = A_t * p_c * coef_empuxo(p_c, p_e, gamma, p_a, A_e / A_t)   # Força de empuxo [unidade: Newton]

    t = cumtrapz(1 / r, x, initial=0)  # tempo em segundos

    return graphic(t, p_c, F)


fire.Fire(empuxo)