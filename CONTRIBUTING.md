# Contribuindo para o WhatsUp Gold OTLP Exporter

Obrigado por considerar contribuir para o WhatsUp Gold OTLP Exporter! Este documento fornece diretrizes e instruções para contribuir.

## Código de Conduta

Este projeto adere a um Código de Conduta. Ao participar, você concorda em manter um ambiente respeitoso e inclusivo.

## Como Contribuir

### Reportando Bugs

Antes de criar um relatório de bug, verifique a lista de issues, pois você pode descobrir que o bug já foi reportado. Ao criar um relatório de bug, inclua:

- **Título descritivo** para o issue
- **Descrição exata do comportamento observado**
- **Comportamento esperado**
- **Passos para reproduzir** o problema
- **Exemplos específicos** para demonstrar os passos
- **Screenshots** (se aplicável)
- **Seu ambiente** (SO, versão Python, versão WhatsUp Gold, etc.)

### Sugerindo Melhorias

Sugestões de melhorias são sempre bem-vindas. Ao criar uma sugestão de melhoria, inclua:

- **Título descritivo**
- **Descrição detalhada** da melhoria sugerida
- **Exemplos de como** a melhoria funcionaria
- **Por que essa melhoria seria útil**

### Pull Requests

- Preencha o template de pull request
- Siga os padrões de código Python (PEP 8)
- Inclua testes apropriados
- Atualize a documentação conforme necessário
- Termine todos os arquivos com uma nova linha

## Processo de Desenvolvimento

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie uma branch** para sua feature (`git checkout -b feature/AmazingFeature`)
4. **Faça seus commits** com mensagens descritivas
5. **Push** para sua branch (`git push origin feature/AmazingFeature`)
6. **Abra um Pull Request**

## Padrões de Código

### Python

- Siga [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints quando possível
- Documente funções e classes com docstrings
- Use logging ao invés de print statements

Exemplo:

```python
def get_devices(self) -> List[Dict]:
    """
    Obter lista de dispositivos do WhatsUp Gold.
    
    Returns:
        List[Dict]: Lista de dispositivos
        
    Raises:
        Exception: Se houver erro na requisição
    """
    try:
        # implementação
        pass
    except Exception as e:
        logger.error(f"Erro ao obter dispositivos: {e}")
        raise
```

### Commits

- Use mensagens de commit descritivas
- Use o imperativo ("Add feature" não "Added feature")
- Limite a primeira linha a 72 caracteres
- Referencie issues quando apropriado

Exemplo:

```
Add support for custom OTLP headers

- Permite configurar headers customizados via variáveis de ambiente
- Útil para autenticação com endpoints OTLP customizados
- Fixes #123
```

### Documentação

- Atualize o README.md se necessário
- Adicione exemplos para novas features
- Documente mudanças de comportamento
- Mantenha a documentação sincronizada com o código

## Testes

- Escreva testes para novas features
- Certifique-se que todos os testes passam
- Mantenha a cobertura de testes acima de 80%

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=wug_otlp_exporter
```

## Revisão de Pull Request

Os maintainers revisarão seu PR e podem solicitar mudanças. Isso é normal e esperado. Mudanças podem ser solicitadas para:

- Manter a qualidade do código
- Garantir consistência com o projeto
- Melhorar a documentação
- Adicionar testes

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a Licença MIT.

## Perguntas?

Sinta-se livre para abrir uma issue com a tag `question` ou entrar em contato com os maintainers.

Obrigado por contribuir! 🎉
