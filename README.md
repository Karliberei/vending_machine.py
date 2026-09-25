# Noxviva Pro — Soyuz Bird Edition 🦅🪙

O **Noxviva Pro** é um software avançado de simulação para máquinas de venda automática (*Vending Machines*) desenvolvido em Python com interface gráfica integrada via **Tkinter**. Esta versão especial inclui um motor económico de flutuação de preços em tempo real, suporte para moedas físicas ajustadas, pagamentos digitais simulados e um modo inovador de **multi-compra**.

---

## ✨ Funcionalidades Principais

- **🛒 Modo Multi-Compra:** O saldo inserido não é reiniciado após cada compra. O utilizador pode comprar vários produtos consecutivamente até decidir recolher o troco acumulado.
- **📈 Atualização de Bolsa (Preços Dinâmicos):** Os preços dos produtos flutuam dinamicamente com base na procura (exceto o botão especial).
- **📱 Pagamento Digital:** Simulação integrada de carregamento instantâneo via **MB WAY**.
- **🎟️ Sistema de Vouchers & NIF:** Suporte para introdução de NIF de cliente válido (9 dígitos) e aplicação de cupões de utilização única.
- **🛡️ Painel Administrativo:** Proteção contra tentativas de invasão e reabastecimento automático em modo de manutenção.
- **💾 Persistência de Estado:** Gravação automática do stock e saldo dos tubos em ficheiros `JSON` e exportação do histórico de faturação para `CSV`.

---

## 🛠️ Especificações Técnicas de Operação

### 🪙 Moedas Aceites nos Tubos
O validador físico da máquina está calibrado para aceitar e processar trocos automáticos com as seguintes moedas:
- `2.00€` | `1.00€` | `0.50€` | `0.20€` | `0.10€` | `0.05€`

### 🔑 Códigos de Acesso e Vouchers de Fábrica
- **Código Admin (Manutenção):** `SOYUZ1967` *(Repõe o stock e moedas para 20 unidades).*
- **Vouchers Disponíveis:** 
  - `DESCONTO10` *(Adiciona 0.50€ de crédito ao saldo).*
  - `PROMOVIP` *(Adiciona 1.00€ de crédito ao saldo).*

---

## 🚀 Como Executar

### Pré-requisitos
- **Python 3.x** instalado.
- Sistema Operativo: Windows (para suporte nativo de áudio `winsound`) ou Linux/macOS.

### Instruções
1. Clone este repositório para a sua máquina local:
   ```bash
   git clone https://github.com
   ```
2. Navegue até à pasta do projeto:
   ```bash
   cd Noxviva-Pro
   ```
3. Execute o script principal da aplicação:
   ```bash
   python vending_machine.py
   ```

---

## 📁 Estrutura de Ficheiros Gerados

Após a primeira execução do sistema, serão criados os seguintes ficheiros na raiz do projeto:
* `vending_state.json`: Base de dados local que guarda o stock atualizado de mercadorias e a quantidade de moedas guardadas em cada tubo.
* `vending_sales_log.csv`: Registo detalhado e auditável de todas as vendas efetuadas (contendo *Timestamp*, *Slot*, *Produto*, *Preço* e *NIF* do cliente).

---

## 📝 Licença

Este projeto é disponibilizado para fins educativos e de simulação interna. Desenvolvido com foco em sistemas embarcados e interfaces industriais personalizadas.
