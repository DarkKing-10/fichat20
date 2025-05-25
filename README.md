# Ficha de Personagem - Tormenta 20
# Character Sheet - Tormenta 20

[English version below](#english-version)

Uma aplicação web interativa para criar e gerenciar fichas de personagem do sistema Tormenta 20, desenvolvida com Streamlit.

## Funcionalidades

### Informações Básicas
- Nome, nível, raça, origem e divindade
- Sistema de multiclasse
- Upload de imagem do personagem
- Tendência

### Atributos
- Força, Destreza, Constituição, Inteligência, Sabedoria e Carisma
- Cálculo automático de modificadores
- Sem limite superior para valores

### Defesa e Deslocamento
- Cálculo automático de defesa
- Opção de usar diferentes atributos para defesa
- Bônus de equipamento e reflexos
- Deslocamento personalizável

### Perícias
- Lista completa de perícias do T20
- Sistema de treinamento
- Seleção de atributo base
- Bônus e penalidades personalizáveis
- Sistema de ofícios adicionais

### Recursos
- Vida, Mana e Prana
- Barras de progresso visuais
- Recursos adicionais personalizáveis
- Cores personalizáveis para recursos

### Inventário
- Sistema de dinheiro (T$, PP, PO, PE, PC)
- Cálculo automático de carga
- Sistema de encumbrance do T20
- Gerenciamento de itens com:
  - Nome, tipo, quantidade, peso e valor
  - Descrições detalhadas
  - Propriedades específicas por tipo de item
  - Bônus em atributos e perícias

### Magias
- Sistema flexível de magias
- Suporte para magias arcanas e divinas
- Níveis de magia ilimitados
- Organização por tipo e nível
- Busca por nome ou descrição
- Detalhes completos de cada magia

### Poderes e Habilidades
- Gerenciamento de poderes
- Gerenciamento de habilidades
- Busca por nome ou descrição
- Seções expansíveis

## Requisitos

- Python 3.7+
- Streamlit
- Pillow (PIL)

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
streamlit run app.py
```

## Uso

1. Abra a aplicação no navegador
2. Preencha as informações do personagem
3. Use o botão "Salvar Ficha" para baixar a ficha em formato JSON
4. Use o botão "Carregar Ficha" para importar uma ficha existente

## Recursos Adicionais

- Compatibilidade com fichas de versões anteriores
- Sistema de busca em magias, poderes e habilidades
- Interface responsiva
- Salvamento automático do estado
- Suporte a imagens de personagem

## Contribuindo

Contribuições são bem-vindas! Por favor, sinta-se à vontade para:
1. Fazer um fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Contato

[Seu Nome] - [Seu Email]

Link do Projeto: [https://github.com/seu-usuario/seu-repositorio](https://github.com/seu-usuario/seu-repositorio)

---

# English Version

A web application developed with Streamlit to create and manage character sheets for the Tormenta 20 system.

## Features

### Basic Information
- Character name, level, and race
- Multiclass system
- Deity and alignment
- Character image upload and display

### Attributes
- Strength, Dexterity, Constitution
- Intelligence, Wisdom, Charisma
- Automatic modifier calculation

### Skills
- Complete list of T20 skills
- Option to mark trained skills
- Choose base attribute for each skill
- Automatic bonus calculation

### Resources
- Life, Mana, and Prana
- Visual progress bars
- Customizable additional resources
- Customizable colors for each resource

### Inventory
- Money system (T$, PP, PO, PE, PC)
- Load management
- Items with detailed properties:
  - Name, type, quantity, weight, and value
  - Descriptions and properties
  - Specific fields for weapons
  - Specific fields for magical items
  - Attribute bonuses
  - Skill bonuses
  - Other bonuses (attack, damage, defense, initiative)

### Spells
- Organization by type (Arcane/Divine)
- Organization by level (1st to 5th)
- Fields for:
  - Name and school
  - Execution, range, and target
  - Duration and resistance
  - Detailed description

### Powers and Abilities
- Name and type
- Cost and requirements
- Detailed description

### Save and Load
- Character sheet export in JSON format
- Import saved character sheets
- Preservation of all information
- Character image support

## Requirements

- Python 3.7+
- Streamlit
- Pillow (PIL)

## Installation

1. Clone the repository:
```bash
git clone [REPOSITORY_URL]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Access the application in your browser (usually at http://localhost:8501)
2. Fill in the character information
3. Use the "Save Sheet" button to export as JSON
4. Use the "Load Sheet" button to import a saved sheet

## Technical Features

- Responsive interface
- Automatic calculation updates
- JSON data persistence
- Base64 image support
- State system to preserve changes

## Contributing

Contributions are welcome! Feel free to:
1. Report bugs
2. Suggest new features
3. Submit pull requests

## License

This project is under the MIT license. See the LICENSE file for more details. 