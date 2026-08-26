using FluentMigrator;

namespace SerenityQuantResearch.Migrations.DefaultDB;

[DefaultDB, MigrationKey(20260825_1000)]
public class DefaultDB_20260825_1000_P3ResearchActorType : AutoReversingMigration
{
    public override void Up()
    {
        Alter.Table("Users")
            .AddColumn("ActorType").AsString(16).NotNullable().WithDefaultValue("human");
    }
}
