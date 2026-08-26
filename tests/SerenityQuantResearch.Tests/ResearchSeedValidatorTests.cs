using SerenityQuantResearch.Research.Domain;
using SerenityQuantResearch.Research.Seed;

namespace SerenityQuantResearch.Tests;

public class ResearchSeedValidatorTests
{
    private static ResearchSeedDocument LoadBaseline()
    {
        var path = Path.Combine(AppContext.BaseDirectory, "SeedData", "cpo-research-seed.json");
        return ResearchSeedValidator.Load(File.ReadAllText(path));
    }

    [Fact]
    public void Baseline_has_frozen_P1_counts_and_draft_example()
    {
        var seed = LoadBaseline();

        Assert.Equal(9, seed.Modules.Count);
        Assert.Equal(21, seed.Parts.Count);
        Assert.Equal(10, seed.ChainNodes.Count);
        Assert.Equal(20, seed.Companies.Count);
        Assert.Equal(EvidenceReviewStates.Draft, seed.ExampleChain.Evidence.ReviewState);
    }

    [Fact]
    public void Recursive_part_hierarchy_rejects_cycles()
    {
        var seed = LoadBaseline();
        seed.Parts[0].ParentPartId = seed.Parts[1].Id;
        seed.Parts[1].ParentPartId = seed.Parts[0].Id;

        var error = Assert.Throws<InvalidDataException>(() => ResearchSeedValidator.Validate(seed));
        Assert.Contains("cycle", error.Message, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void Machine_seed_cannot_enter_reviewed_state()
    {
        var seed = LoadBaseline();
        seed.ExampleChain.Evidence.ReviewState = EvidenceReviewStates.Reviewed;

        var error = Assert.Throws<InvalidDataException>(() => ResearchSeedValidator.Validate(seed));
        Assert.Contains("must start as draft", error.Message);
    }
}
