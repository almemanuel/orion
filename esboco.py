

# Evolução da área de combustão
def __areaCombustao__(r_ex, r_in, L):
    x = np.linspace(0, r_ex - r_in)    # Distância em relação ao menor raio em direção ao maior raio, dividido em 50 segmentos [unidade: metro].
    A_b = 2 * np.pi * (r_in + x) * L   # Área do combustivel sendo queimada por segmento [unidade: metro**2].
    K = A_b / A_t     # Razão da Área de Combustão (A_b) e Área da garganta (A_t)
    return{'x': x, 'A_b': A_b, 'K': K}

def empuxo(r_in = 0.015, r_ex = 0.044, L = 1.10, D_t = 0.00708):
    r_in = __is_valid__(r_in, 'raio interno')
    r_ex = __is_valid__(r_ex, 'raio externo')
    L = __is_valid__(L, 'comprimento')

    D_t = __is_valid__(D_t, 'diametro da garganta')
    A_t = np.pi*((D_t)**2)
    A_e = 3.94e-5

    area_combustao = __areaCombustao__

    c = nozzle.c_star(gamma, m_molar, T_c)

    p_c = solid.chamber_pressure(A_b / A_t, a, n, rho_solid, c) # [unidade: pascal]

    r = a * p_c**n

    p_e = p_c * __RazaoPressoes__(A_e / A_t, gamma) #[unidade: pascal]

    p_a = 101325    # Pressão do ambiente [unidade: pascal]
    F = A_t * p_c * __thrust_coef__(p_c, p_e, gamma, p_a, A_e / A_t)   # Força de empuxo [unidade: Newton]

    t = cumtrapz(1 / r, x, initial=0)  # [unidade: segundos]

    ax1 = plt.subplot(2, 1, 1)
    plt.plot(t, p_c * 1e-6)
    plt.ylabel('Chamber pressure [MPa]')

    ax2 = plt.subplot(2, 1, 2)
    plt.plot(t, F * 1e-3)
    plt.ylabel('Thrust, sea level [kN]')
    plt.xlabel('Time [s]')
    plt.setp(ax1.get_xticklabels(), visible=False)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0)
    return plt.show()