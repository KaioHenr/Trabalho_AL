"""Funções genéricas de cadeias de Markov de estados finitos.

Convenções usadas em todo o módulo:
- P é uma matriz n x n estocástica por LINHAS: P[i, j] = Pr(X_{t+1} = j | X_t = i).
- Distribuições de probabilidade são vetores-LINHA, e evoluem por pi_{t+1} = pi_t @ P.
- Os estados são indexados a partir de 0 no código: o nível de alerta 1 (verde)
  é o índice 0, ..., o nível 4 (vermelho) é o índice 3.

As funções de dados (leitura de CSV, contagem de transições) ficam nos scripts
das etapas; aqui só há matemática, validada contra a Tabela 1 do enunciado.
"""

import numpy as np


# [IA] Claude Code (claude-opus-5-5) – 2026-11-18 – validação de matriz estocástica
def is_stochastic(P, tol=1e-12):
    """Verifica se P >= 0 (entrada a entrada) e P @ 1 = 1 (cada linha soma 1), com tolerância tol."""
    P = np.asarray(P, dtype=float)
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        return False
    nao_negativa = np.all(P >= -tol)
    linhas_somam_1 = np.all(np.abs(P.sum(axis=1) - 1.0) <= tol)
    return bool(nao_negativa and linhas_somam_1)
# [/IA]


# [IA] Claude Code (claude-opus-5-5) – 2026-11-18 – distribuição estacionária por três caminhos
def stationary_linear(P):
    """Distribuição estacionária pi resolvendo o sistema linear (P^T - I) pi^T = 0.

    O sistema homogêneo é singular (tem infinitas soluções). Substituímos a
    última equação pela normalização pi_1 + ... + pi_n = 1, o que torna a
    solução única quando 1 é autovalor simples. O sistema é resolvido por
    numpy.linalg.solve (fatoração LU com pivotamento parcial).
    """
    P = np.asarray(P, dtype=float)
    n = P.shape[0]
    A = P.T - np.eye(n)
    A[-1, :] = 1.0          # última equação vira: soma das entradas = 1
    b = np.zeros(n)
    b[-1] = 1.0
    return np.linalg.solve(A, b)


def stationary_eig(P):
    """Distribuição estacionária como autovetor à ESQUERDA de P associado a lambda = 1.

    Autovetor à esquerda de P (pi P = pi) é o mesmo que autovetor à direita de
    P^T (P^T pi^T = pi^T). numpy.linalg.eig calcula todos os autovetores de P^T
    (algoritmo QR sobre a forma de Hessenberg); escolhemos o do autovalor mais
    próximo de 1 e o normalizamos para somar 1.
    """
    P = np.asarray(P, dtype=float)
    autovalores, autovetores = np.linalg.eig(P.T)
    k = np.argmin(np.abs(autovalores - 1.0))
    v = np.real(autovetores[:, k])
    return v / v.sum()


def stationary_power(P, pi0, tol=1e-12, max_iter=1_000_000):
    """Método das potências, escrito explicitamente: pi^(k+1) = pi^(k) P.

    Repete a multiplicação até ||pi^(k+1) - pi^(k)||_1 < tol.
    Devolve (pi, número de iterações feitas).
    """
    P = np.asarray(P, dtype=float)
    pi = np.asarray(pi0, dtype=float)
    for k in range(1, max_iter + 1):
        novo = pi @ P
        if np.sum(np.abs(novo - pi)) < tol:
            return novo, k
        pi = novo
    raise RuntimeError(f"método das potências não convergiu em {max_iter} iterações")
# [/IA]


# [IA] Claude Code (claude-opus-5-5) – 2026-11-18 – espectro, meia-vida e primitividade
def spectrum(P):
    """Autovalores de P ordenados por módulo decrescente (lambda_1 = 1 vem primeiro)."""
    autovalores = np.linalg.eigvals(np.asarray(P, dtype=float))
    ordem = np.argsort(-np.abs(autovalores), kind="stable")
    return autovalores[ordem]


def half_life(P):
    """Meia-vida n_1/2 = ln(1/2) / ln|lambda_2|, em semanas.

    É o número de passos para a parcela mais lenta da distância até pi cair à metade.
    """
    lambda2 = np.abs(spectrum(P)[1])
    return np.log(0.5) / np.log(lambda2)


def min_k_positive(P, k_max=None):
    """Menor k tal que P^k > 0 em todas as entradas (P é primitiva).

    As potências são calculadas por multiplicação repetida explícita.
    Por padrão, testa até o limite de Wielandt (n-1)^2 + 1: se P^k ainda tiver
    zero nesse ponto, P não é primitiva e a função devolve None.
    """
    P = np.asarray(P, dtype=float)
    n = P.shape[0]
    if k_max is None:
        k_max = (n - 1) ** 2 + 1
    Pk = P.copy()
    for k in range(1, k_max + 1):
        if np.all(Pk > 0):
            return k
        Pk = Pk @ P
    return None
# [/IA]


# [IA] Claude Code (claude-opus-5-5) – 2026-11-18 – potências de matriz por três caminhos
def power_repeated(P, n):
    """P^n por multiplicação repetida: P @ P @ ... @ P (n vezes), em laço explícito."""
    P = np.asarray(P, dtype=float)
    resultado = np.eye(P.shape[0])
    for _ in range(n):
        resultado = resultado @ P
    return resultado


def power_squaring(P, n):
    """P^n por quadrados sucessivos, em laço explícito.

    Escreve n em binário: P^13 = P^8 @ P^4 @ P^1. A cada passo a base é elevada
    ao quadrado (P, P^2, P^4, P^8, ...) e, quando o bit de n é 1, ela entra no
    produto. Usa cerca de 2*log2(n) multiplicações em vez de n.
    """
    P = np.asarray(P, dtype=float)
    resultado = np.eye(P.shape[0])
    base = P.copy()
    while n > 0:
        if n % 2 == 1:
            resultado = resultado @ base
        base = base @ base
        n //= 2
    return resultado


def power_diag(P, n):
    """P^n por diagonalização: P = V Lambda V^-1  =>  P^n = V Lambda^n V^-1.

    Devolve (P^n, kappa_1(V)), em que kappa_1(V) = ||V||_1 ||V^-1||_1 é o número
    de condição de V: quanto maior, menos confiável é a conta numericamente.
    Se P tiver autovalores complexos, eles vêm em pares conjugados e a parte
    imaginária do resultado é só erro de arredondamento, descartada no final.
    """
    P = np.asarray(P, dtype=float)
    autovalores, V = np.linalg.eig(P)
    V_inv = np.linalg.inv(V)
    Pn = V @ np.diag(autovalores ** n) @ V_inv
    kappa1 = np.linalg.norm(V, 1) * np.linalg.norm(V_inv, 1)
    return np.real(Pn), kappa1
# [/IA]


# [IA] Claude Code (claude-opus-5-5) – 2026-11-18 – tempos médios de primeira passagem
def first_passage_systems(P):
    """Matriz M de tempos médios de primeira passagem, resolvendo n sistemas lineares.

    Para cada estado-alvo j, as incógnitas m_ij (i != j) satisfazem
        m_ij = 1 + sum_{k != j} p_ik m_kj,
    ou seja, (I - P_sem_j) m = 1, em que P_sem_j é P sem a linha e a coluna j.
    Com 4 estados, são 4 sistemas 3x3. A diagonal (tempo médio de retorno) vem
    da mesma condição sobre o primeiro passo: m_jj = 1 + sum_{k != j} p_jk m_kj.
    A fórmula de Kac (m_jj = 1/pi_j) NÃO é usada aqui; ela serve de conferência.
    """
    P = np.asarray(P, dtype=float)
    n = P.shape[0]
    M = np.zeros((n, n))
    for j in range(n):
        outros = [k for k in range(n) if k != j]
        P_sem_j = P[np.ix_(outros, outros)]
        m = np.linalg.solve(np.eye(n - 1) - P_sem_j, np.ones(n - 1))
        M[outros, j] = m
        M[j, j] = 1.0 + P[j, outros] @ m
    return M


def first_passage_fundamental(P):
    """Matriz M pela matriz fundamental Z = (I - P + 1 pi)^-1 (segundo caminho).

    m_ij = (z_jj - z_ij) / pi_j para i != j, e m_jj = 1 / pi_j (Kac).
    """
    P = np.asarray(P, dtype=float)
    n = P.shape[0]
    pi = stationary_linear(P)
    Z = np.linalg.inv(np.eye(n) - P + np.outer(np.ones(n), pi))
    M = (np.diag(Z)[np.newaxis, :] - Z) / pi[np.newaxis, :]
    M[np.diag_indices(n)] = 1.0 / pi
    return M
# [/IA]


# [IA] Claude Code (claude-opus-5-5) – 2026-11-18 – cadeia absorvente e série de Neumann
def absorbing_analysis(P, absorventes):
    """Análise de cadeia absorvente.

    `absorventes` é a lista de índices (base 0) dos estados tornados absorventes;
    os demais são transientes, na ordem original. Com P = [[Q, R], [0, I]]:
      N   = (I - Q)^-1             número esperado de visitas a cada transiente
      t   = N 1                    tempo médio até a absorção
      var = (2N - I) t - t∘t       variância desse tempo (∘ = produto entrada a entrada)
      B   = N R                    probabilidade de absorção em cada absorvente
    Devolve um dicionário com transientes, absorventes, Q, R, N, t, var, B.
    """
    P = np.asarray(P, dtype=float)
    n = P.shape[0]
    absorventes = list(absorventes)
    transientes = [k for k in range(n) if k not in absorventes]
    Q = P[np.ix_(transientes, transientes)]
    R = P[np.ix_(transientes, absorventes)]
    N = np.linalg.inv(np.eye(len(transientes)) - Q)
    t = N @ np.ones(len(transientes))
    var = (2 * N - np.eye(len(transientes))) @ t - t * t
    B = N @ R
    return {"transientes": transientes, "absorventes": absorventes,
            "Q": Q, "R": R, "N": N, "t": t, "var": var, "B": B}


def neumann_partial(Q, K):
    """Soma parcial da série de Neumann: I + Q + Q^2 + ... + Q^K, em laço explícito.

    Quando ||Q^m|| < 1 para algum m, essa soma converge para (I - Q)^-1 = N.
    """
    Q = np.asarray(Q, dtype=float)
    termo = np.eye(Q.shape[0])   # Q^0
    soma = termo.copy()
    for _ in range(K):
        termo = termo @ Q
        soma = soma + termo
    return soma
# [/IA]


# [IA] Claude Code (claude-opus-5-5) – 2026-11-25 – curva de convergência para pi
def convergence_curve(P, pi0, pi, n_max):
    """Distâncias d(n) = ||pi0 P^n - pi||_1 para n = 0, 1, ..., n_max.

    A distribuição é atualizada passo a passo (pi^(n+1) = pi^(n) P), em laço explícito.
    Se P é diagonalizável, d(n) decai como C |lambda_2|^n.
    """
    P = np.asarray(P, dtype=float)
    dist = np.asarray(pi0, dtype=float)
    pi = np.asarray(pi, dtype=float)
    d = np.empty(n_max + 1)
    for n in range(n_max + 1):
        d[n] = np.sum(np.abs(dist - pi))
        dist = dist @ P
    return d
# [/IA]
