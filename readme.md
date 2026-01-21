ftbb/
│
├── FTBB.sln                                    # Main Solution File
├── docker-compose.yml
├── docker-compose.override.yml
├── .dockerignore
├── .gitignore
├── README.md
├── global.json
├── Directory.Build.props
├── nuget.config
│
├── src/
│   │
│   ├── Gateway/
│   │   └── FTBB.Gateway/                       # ASP.NET Core (Ocelot Gateway)
│   │       ├── FTBB.Gateway.csproj
│   │       ├── Program.cs
│   │       ├── ocelot.json
│   │       ├── appsettings.json
│   │       ├── appsettings.Development.json
│   │       ├── Properties/
│   │       │   └── launchSettings.json
│   │       └── Dockerfile
│   │
│   ├── Services/
│   │   │
│   │   ├── Auth/
│   │   │   ├── FTBB.Auth.API/                  # ASP.NET Core Web API
│   │   │   │   ├── FTBB.Auth.API.csproj
│   │   │   │   ├── Program.cs
│   │   │   │   ├── Controllers/
│   │   │   │   │   ├── AuthController.cs
│   │   │   │   │   └── UsersController.cs
│   │   │   │   ├── Models/
│   │   │   │   │   ├── Requests/
│   │   │   │   │   │   ├── LoginRequest.cs
│   │   │   │   │   │   └── RegisterRequest.cs
│   │   │   │   │   └── Responses/
│   │   │   │   │       └── AuthResponse.cs
│   │   │   │   ├── Middleware/
│   │   │   │   │   ├── JwtMiddleware.cs
│   │   │   │   │   └── ExceptionMiddleware.cs
│   │   │   │   ├── Configuration/
│   │   │   │   │   └── JwtSettings.cs
│   │   │   │   ├── appsettings.json
│   │   │   │   ├── Dockerfile
│   │   │   │   └── Properties/
│   │   │   │
│   │   │   ├── FTBB.Auth.Domain/               # Class Library
│   │   │   │   ├── FTBB.Auth.Domain.csproj
│   │   │   │   ├── Entities/
│   │   │   │   │   ├── User.cs
│   │   │   │   │   ├── Role.cs
│   │   │   │   │   └── Permission.cs
│   │   │   │   ├── Interfaces/
│   │   │   │   │   └── IUserRepository.cs
│   │   │   │   └── Enums/
│   │   │   │       └── UserRole.cs
│   │   │   │
│   │   │   ├── FTBB.Auth.Application/          # Class Library
│   │   │   │   ├── FTBB.Auth.Application.csproj
│   │   │   │   ├── Services/
│   │   │   │   │   ├── AuthService.cs
│   │   │   │   │   ├── TokenService.cs
│   │   │   │   │   └── UserService.cs
│   │   │   │   ├── Interfaces/
│   │   │   │   │   ├── IAuthService.cs
│   │   │   │   │   └── ITokenService.cs
│   │   │   │   ├── DTOs/
│   │   │   │   │   ├── UserDto.cs
│   │   │   │   │   └── TokenDto.cs
│   │   │   │   └── Validators/
│   │   │   │       └── LoginRequestValidator.cs
│   │   │   │
│   │   │   └── FTBB.Auth.Infrastructure/       # Class Library
│   │   │       ├── FTBB.Auth.Infrastructure.csproj
│   │   │       ├── Data/
│   │   │       │   ├── AuthDbContext.cs
│   │   │       │   └── Configurations/
│   │   │       │       ├── UserConfiguration.cs
│   │   │       │       └── RoleConfiguration.cs
│   │   │       ├── Repositories/
│   │   │       │   └── UserRepository.cs
│   │   │       └── Migrations/
│   │   │
│   │   ├── PdfWorker/
│   │   │   ├── FTBB.PdfWorker.Service/         # Worker Service
│   │   │   │   ├── FTBB.PdfWorker.Service.csproj
│   │   │   │   ├── Program.cs
│   │   │   │   ├── Workers/
│   │   │   │   │   ├── PdfIngestionWorker.cs
│   │   │   │   │   └── PdfProcessorWorker.cs
│   │   │   │   ├── appsettings.json
│   │   │   │   ├── Dockerfile
│   │   │   │   └── Properties/
│   │   │   │
│   │   │   ├── FTBB.PdfWorker.Domain/          # Class Library
│   │   │   │   ├── FTBB.PdfWorker.Domain.csproj
│   │   │   │   ├── Entities/
│   │   │   │   │   ├── PdfDocument.cs
│   │   │   │   │   └── DocumentLine.cs
│   │   │   │   └── Enums/
│   │   │   │       └── ProcessingStatus.cs
│   │   │   │
│   │   │   ├── FTBB.PdfWorker.Application/     # Class Library
│   │   │   │   ├── FTBB.PdfWorker.Application.csproj
│   │   │   │   ├── Services/
│   │   │   │   │   ├── PdfExtractorService.cs
│   │   │   │   │   ├── PdfParserService.cs
│   │   │   │   │   └── StorageService.cs
│   │   │   │   └── Interfaces/
│   │   │   │       ├── IPdfExtractorService.cs
│   │   │   │       └── IPdfParserService.cs
│   │   │   │
│   │   │   └── FTBB.PdfWorker.Infrastructure/  # Class Library
│   │   │       ├── FTBB.PdfWorker.Infrastructure.csproj
│   │   │       ├── Queue/
│   │   │       │   ├── RabbitMqPublisher.cs
│   │   │       │   └── RabbitMqConsumer.cs
│   │   │       └── FileSystem/
│   │   │           └── LocalFileStorage.cs
│   │   │
│   │   ├── Storage/
│   │   │   ├── FTBB.Storage.API/               # ASP.NET Core Web API
│   │   │   │   ├── FTBB.Storage.API.csproj
│   │   │   │   ├── Program.cs
│   │   │   │   ├── Controllers/
│   │   │   │   │   └── DocumentsController.cs
│   │   │   │   ├── appsettings.json
│   │   │   │   ├── Dockerfile
│   │   │   │   └── Properties/
│   │   │   │
│   │   │   ├── FTBB.Storage.Domain/            # Class Library
│   │   │   │   ├── FTBB.Storage.Domain.csproj
│   │   │   │   ├── Entities/
│   │   │   │   │   ├── Document.cs
│   │   │   │   │   └── DocumentLine.cs
│   │   │   │   └── Interfaces/
│   │   │   │       └── IDocumentRepository.cs
│   │   │   │
│   │   │   ├── FTBB.Storage.Application/       # Class Library
│   │   │   │   ├── FTBB.Storage.Application.csproj
│   │   │   │   ├── Services/
│   │   │   │   │   ├── DocumentService.cs
│   │   │   │   │   └── SearchService.cs
│   │   │   │   └── DTOs/
│   │   │   │       └── DocumentDto.cs
│   │   │   │
│   │   │   └── FTBB.Storage.Infrastructure/    # Class Library
│   │   │       ├── FTBB.Storage.Infrastructure.csproj
│   │   │       ├── Data/
│   │   │       │   ├── StorageDbContext.cs
│   │   │       │   └── Configurations/
│   │   │       ├── Repositories/
│   │   │       │   └── DocumentRepository.cs
│   │   │       └── Migrations/
│   │   │
│   │   ├── Teams/
│   │   │   ├── FTBB.Teams.API/                 # ASP.NET Core Web API
│   │   │   │   ├── FTBB.Teams.API.csproj
│   │   │   │   ├── Program.cs
│   │   │   │   ├── Controllers/
│   │   │   │   │   ├── TeamsController.cs
│   │   │   │   │   └── RankingsController.cs
│   │   │   │   ├── appsettings.json
│   │   │   │   ├── Dockerfile
│   │   │   │   └── Properties/
│   │   │   │
│   │   │   ├── FTBB.Teams.Domain/              # Class Library
│   │   │   │   ├── FTBB.Teams.Domain.csproj
│   │   │   │   ├── Entities/
│   │   │   │   │   ├── Team.cs
│   │   │   │   │   ├── TeamStats.cs
│   │   │   │   │   └── Ranking.cs
│   │   │   │   └── Interfaces/
│   │   │   │       └── ITeamRepository.cs
│   │   │   │
│   │   │   ├── FTBB.Teams.Application/         # Class Library
│   │   │   │   ├── FTBB.Teams.Application.csproj
│   │   │   │   ├── Services/
│   │   │   │   │   ├── TeamService.cs
│   │   │   │   │   ├── RankingService.cs
│   │   │   │   │   └── CacheService.cs
│   │   │   │   ├── DTOs/
│   │   │   │   │   ├── TeamDto.cs
│   │   │   │   │   └── RankingDto.cs
│   │   │   │   └── Events/
│   │   │   │       ├── TeamCreatedEvent.cs
│   │   │   │       └── RankingUpdatedEvent.cs
│   │   │   │
│   │   │   └── FTBB.Teams.Infrastructure/      # Class Library
│   │   │       ├── FTBB.Teams.Infrastructure.csproj
│   │   │       ├── Data/
│   │   │       │   ├── TeamsDbContext.cs
│   │   │       │   └── Configurations/
│   │   │       ├── Repositories/
│   │   │       │   └── TeamRepository.cs
│   │   │       ├── Cache/
│   │   │       │   └── RedisCache.cs
│   │   │       └── Migrations/
│   │   │
│   │   └── Stats/
│   │       ├── FTBB.Stats.API/                 # ASP.NET Core Web API
│   │       │   ├── FTBB.Stats.API.csproj
│   │       │   ├── Program.cs
│   │       │   ├── Controllers/
│   │       │   │   ├── PlayersController.cs
│   │       │   │   └── StatsController.cs
│   │       │   ├── appsettings.json
│   │       │   ├── Dockerfile
│   │       │   └── Properties/
│   │       │
│   │       ├── FTBB.Stats.Domain/              # Class Library
│   │       │   ├── FTBB.Stats.Domain.csproj
│   │       │   ├── Entities/
│   │       │   │   ├── Player.cs
│   │       │   │   └── PlayerStats.cs
│   │       │   └── Interfaces/
│   │       │       └── IPlayerRepository.cs
│   │       │
│   │       ├── FTBB.Stats.Application/         # Class Library
│   │       │   ├── FTBB.Stats.Application.csproj
│   │       │   ├── Services/
│   │       │   │   ├── PlayerService.cs
│   │       │   │   ├── StatsService.cs
│   │       │   │   └── AggregationService.cs
│   │       │   └── DTOs/
│   │       │       ├── PlayerDto.cs
│   │       │       └── StatsDto.cs
│   │       │
│   │       └── FTBB.Stats.Infrastructure/      # Class Library
│   │           ├── FTBB.Stats.Infrastructure.csproj
│   │           ├── Data/
│   │           │   ├── StatsDbContext.cs
│   │           │   └── Configurations/
│   │           ├── Repositories/
│   │           │   └── PlayerRepository.cs
│   │           └── Migrations/
│   │
│   ├── BuildingBlocks/                          # Shared Libraries
│   │   │
│   │   ├── FTBB.Common/                        # Class Library
│   │   │   ├── FTBB.Common.csproj
│   │   │   ├── Constants/
│   │   │   │   └── AppConstants.cs
│   │   │   ├── Exceptions/
│   │   │   │   ├── BusinessException.cs
│   │   │   │   └── NotFoundException.cs
│   │   │   ├── Extensions/
│   │   │   │   └── StringExtensions.cs
│   │   │   └── Helpers/
│   │   │       └── DateTimeHelper.cs
│   │   │
│   │   ├── FTBB.EventBus/                      # Class Library
│   │   │   ├── FTBB.EventBus.csproj
│   │   │   ├── Abstractions/
│   │   │   │   ├── IEventBus.cs
│   │   │   │   └── IntegrationEvent.cs
│   │   │   ├── Events/
│   │   │   │   ├── PdfUploadedEvent.cs
│   │   │   │   ├── PdfProcessedEvent.cs
│   │   │   │   ├── TeamCreatedEvent.cs
│   │   │   │   └── StatsUpdatedEvent.cs
│   │   │   └── RabbitMQ/
│   │   │       ├── RabbitMqEventBus.cs
│   │   │       └── RabbitMqConnection.cs
│   │   │
│   │   └── FTBB.SharedKernel/                  # Class Library
│   │       ├── FTBB.SharedKernel.csproj
│   │       ├── BaseEntity.cs
│   │       ├── IAggregateRoot.cs
│   │       ├── IRepository.cs
│   │       └── ValueObject.cs
│   │
│   └── Web/
│       └── FTBB.Web/                            # Angular Application
│           ├── angular.json
│           ├── package.json
│           ├── tsconfig.json
│           ├── tsconfig.app.json
│           ├── tsconfig.spec.json
│           ├── Dockerfile
│           ├── .editorconfig
│           ├── .gitignore
│           ├── src/
│           │   ├── index.html
│           │   ├── main.ts
│           │   ├── styles.scss
│           │   ├── environments/
│           │   │   ├── environment.ts
│           │   │   └── environment.prod.ts
│           │   ├── app/
│           │   │   ├── app.module.ts
│           │   │   ├── app.component.ts
│           │   │   ├── app.component.html
│           │   │   ├── app.component.scss
│           │   │   ├── app-routing.module.ts
│           │   │   │
│           │   │   ├── core/
│           │   │   │   ├── core.module.ts
│           │   │   │   ├── services/
│           │   │   │   │   ├── auth.service.ts
│           │   │   │   │   ├── http.service.ts
│           │   │   │   │   └── storage.service.ts
│           │   │   │   ├── guards/
│           │   │   │   │   ├── auth.guard.ts
│           │   │   │   │   └── role.guard.ts
│           │   │   │   ├── interceptors/
│           │   │   │   │   ├── jwt.interceptor.ts
│           │   │   │   │   └── error.interceptor.ts
│           │   │   │   └── models/
│           │   │   │       ├── user.model.ts
│           │   │   │       └── api-response.model.ts
│           │   │   │
│           │   │   ├── shared/
│           │   │   │   ├── shared.module.ts
│           │   │   │   ├── components/
│           │   │   │   │   ├── header/
│           │   │   │   │   ├── footer/
│           │   │   │   │   ├── sidebar/
│           │   │   │   │   └── loading/
│           │   │   │   ├── directives/
│           │   │   │   │   └── permission.directive.ts
│           │   │   │   ├── pipes/
│           │   │   │   │   └── safe-html.pipe.ts
│           │   │   │   └── validators/
│           │   │   │       └── custom.validators.ts
│           │   │   │
│           │   │   ├── features/
│           │   │   │   ├── auth/
│           │   │   │   │   ├── auth.module.ts
│           │   │   │   │   ├── auth-routing.module.ts
│           │   │   │   │   ├── components/
│           │   │   │   │   │   ├── login/
│           │   │   │   │   │   └── register/
│           │   │   │   │   └── services/
│           │   │   │   │       └── auth-api.service.ts
│           │   │   │   │
│           │   │   │   ├── documents/
│           │   │   │   │   ├── documents.module.ts
│           │   │   │   │   ├── documents-routing.module.ts
│           │   │   │   │   ├── components/
│           │   │   │   │   │   ├── upload/
│           │   │   │   │   │   ├── list/
│           │   │   │   │   │   └── detail/
│           │   │   │   │   ├── services/
│           │   │   │   │   │   └── document.service.ts
│           │   │   │   │   └── models/
│           │   │   │   │       └── document.model.ts
│           │   │   │   │
│           │   │   │   ├── teams/
│           │   │   │   │   ├── teams.module.ts
│           │   │   │   │   ├── teams-routing.module.ts
│           │   │   │   │   ├── components/
│           │   │   │   │   │   ├── team-list/
│           │   │   │   │   │   ├── team-detail/
│           │   │   │   │   │   └── rankings/
│           │   │   │   │   ├── services/
│           │   │   │   │   │   └── team.service.ts
│           │   │   │   │   └── models/
│           │   │   │   │       ├── team.model.ts
│           │   │   │   │       └── ranking.model.ts
│           │   │   │   │
│           │   │   │   └── stats/
│           │   │   │       ├── stats.module.ts
│           │   │   │       ├── stats-routing.module.ts
│           │   │   │       ├── components/
│           │   │   │       │   ├── player-list/
│           │   │   │       │   ├── player-detail/
│           │   │   │       │   └── statistics/
│           │   │   │       ├── services/
│           │   │   │       │   └── stats.service.ts
│           │   │   │       └── models/
│           │   │   │           ├── player.model.ts
│           │   │   │           └── stats.model.ts
│           │   │   │
│           │   │   └── layout/
│           │   │       ├── layout.module.ts
│           │   │       └── components/
│           │   │           ├── main-layout/
│           │   │           └── auth-layout/
│           │   │
│           │   └── assets/
│           │       ├── images/
│           │       ├── icons/
│           │       └── styles/
│           │
│           └── nginx/
│               └── nginx.conf
│
├── tests/
│   ├── FTBB.UnitTests/                          # xUnit Test Project
│   │   ├── FTBB.UnitTests.csproj
│   │   ├── Auth/
│   │   │   └── AuthServiceTests.cs
│   │   ├── Teams/
│   │   │   └── TeamServiceTests.cs
│   │   └── Stats/
│   │       └── StatsServiceTests.cs
│   │
│   ├── FTBB.IntegrationTests/                   # xUnit Test Project
│   │   ├── FTBB.IntegrationTests.csproj
│   │   ├── Auth/
│   │   │   └── AuthApiTests.cs
│   │   ├── PdfWorker/
│   │   │   └── PdfProcessingTests.cs
│   │   └── Helpers/
│   │       └── TestWebApplicationFactory.cs
│   │
│   └── FTBB.E2ETests/                           # xUnit Test Project
│       ├── FTBB.E2ETests.csproj
│       └── Scenarios/
│           └── FullWorkflowTests.cs
│
└── infrastructure/
    ├── database/
    │   ├── init-scripts/
    │   │   ├── 01-create-databases.sql
    │   │   └── 02-create-users.sql
    │   └── migrations/
    │
    ├── queue/
    │   ├── rabbitmq.conf
    │   └── definitions.json
    │
    └── monitoring/
        ├── prometheus.yml
        └── grafana/
            └── dashboards/