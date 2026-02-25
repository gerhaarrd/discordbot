# Sistema de Reputação Avançado

Um sistema completo de reputação para bots Discord com controle anti-abuso, histórico e ranking.

## 🚀 Funcionalidades

### Comandos Disponíveis

#### `/rep <usuario> [motivo]`
- **Descrição**: Dá um ponto de reputação para um usuário
- **Parâmetros**:
  - `usuario`: Usuário que receberá a reputação (obrigatório)
  - `motivo`: Motivo da reputação (opcional)
- **Regras**:
  - Não pode dar reputação para si mesmo
  - Não pode dar reputação para bots
  - Cooldown global de 3 horas por usuário que concede
  - Cooldown de 6 horas para o mesmo par (giver → receiver)
  - Bloqueio de troca mútua por 3 horas

#### `/reppoints [usuario]`
- **Descrição**: Mostra a reputação total e posição no ranking
- **Parâmetros**:
  - `usuario`: Usuário para consultar (opcional, padrão: você mesmo)
- **Retorna**:
  - Reputação total
  - Posição no ranking do servidor
  - Barra de progresso visual

#### `/reptop`
- **Descrição**: Mostra o ranking dos 10 usuários com mais reputação
- **Retorna**:
  - Top 10 com medalhas para os 3 primeiros
  - Sua posição no ranking
  - Total de usuários registrados

#### `/rephistory [usuario]`
- **Descrição**: Mostra o histórico das últimas 5 reputações recebidas
- **Parâmetros**:
  - `usuario`: Usuário para consultar (opcional, padrão: você mesmo)
- **Retorna**:
  - Últimas 5 reputações recebidas
  - Quem deu, quando e o motivo

## 🛡️ Sistema Anti-Abuso

### Cooldowns Implementados

1. **Cooldown Global (3h)**
   - Cada usuário só pode dar reputação a cada 3 horas
   - Impede spam de reputação

2. **Cooldown por Par (6h)**
   - Mesmo giver não pode dar rep para o mesmo receiver em 6h
   - Evita "farming" entre amigos

3. **Bloqueio Mútuo (3h)**
   - Se A deu rep para B, B não pode dar rep para A em 3h
   - Impede trocas imediatas

### Validações

- ✅ Auto-reputação bloqueada
- ✅ Reputação para bots bloqueada
- ✅ Validação de servidor
- ✅ Tratamento de erros

## 📊 Estrutura de Dados

### Formato JSON (`rep_users.json`)

```json
{
  "users": {
    "user_id": {
      "rep_total": 0,
      "history": [
        {
          "giver_id": "user_id",
          "receiver_id": "user_id", 
          "reason": "motivo",
          "timestamp": 1234567890,
          "guild_id": "guild_id"
        }
      ],
      "received_from": {},
      "given_to": {}
    }
  },
  "cooldowns": {
    "global": {},
    "pairs": {},
    "mutual": {}
  }
}
```

## 🔧 Instalação e Configuração

### 1. Dependências

O sistema usa as seguintes dependências (já incluídas em `requirements.txt`):
- `discord.py==2.6.4`
- `python-dotenv==1.2.1`

### 2. Configuração

O módulo está configurado para funcionar com o GUILD_ID específico:
- **Guild ID**: `1389947780683796701`

Para alterar, modifique o parâmetro `guild` em cada comando no arquivo `commands/reputation.py`.

### 3. Arquivos Criados

- `commands/reputation.py`: Módulo principal do sistema
- `rep_users.json`: Banco de dados JSON (criado automaticamente)

## 🎯 Exemplos de Uso

### Dar Reputação
```
/rep @usuario "Ajudou no canal de ajuda"
```

### Ver Pontos
```
/reppoints
/reppoints @usuario
```

### Ver Ranking
```
/reptop
```

### Ver Histórico
```
/rephistory
/rephistory @usuario
```

## 🔮 Futuras Implementações

### Cargos Automáticos
A estrutura já está preparada para integração com cargos automáticos baseados em reputação:

```python
# Exemplo de implementação futura
async def check_role_assignments(user_id: int, rep_total: int):
    if rep_total >= 100:
        # Atribuir cargo "Reputado"
        pass
    elif rep_total >= 50:
        # Atribuir cargo "Respeitado"
        pass
```

### Estatísticas Avançadas
- Gráficos de evolução de reputação
- Estatísticas por mês/semana
- Badges especiais

### Sistema de Badges
- Badges por contribuições específicas
- Badges temporárias
- Sistema de níveis

## 🐛 Troubleshooting

### Comandos não aparecem
1. Verifique se o GUILD_ID está correto
2. Reinicie o bot após adicionar o módulo
3. Verifique se não há erros no console

### Erro ao salvar dados
1. Verifique permissões de escrita no arquivo `rep_users.json`
2. Certifique-se de que o diretório está acessível

### Cooldowns não funcionando
1. Verifique o formato do arquivo JSON
2. Reinicie o bot para recarregar os dados

## 📝 Notas de Desenvolvimento

### Arquitetura
- **Modular**: Sistema separado em módulo próprio
- **Escalável**: Estrutura preparada para expansão
- **Seguro**: Múltiplas camadas de validação
- **Performance**: Otimizado para múltiplos servidores

### Boas Práticas
- Código limpo e documentado
- Tratamento de exceções
- Validação de dados
- Interface amigável com embeds

---

**Desenvolvido para portfólio - Sistema completo e pronto para produção**
