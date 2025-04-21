#include <gtest/gtest.h>
#include <random>
#include <algorithm>
#include "treap.cpp"          

/* ------------------------------------------------------------
 *  Test fixture reproducing the Python suite
 * ------------------------------------------------------------ */
class TreapTest : public ::testing::Test {
protected:
    Treap t;
    std::vector<int> data;          // always mirrors keys in the treap
    std::mt19937 rng{ std::random_device{}() };

    void SetUp() override
    {
        /* 1 000 distinct keys in [0, 5000) */
        std::vector<int> all(5000);
        std::iota(all.begin(), all.end(), 0);
        std::shuffle(all.begin(), all.end(), rng);

        data.assign(all.begin(), all.begin() + 1000);
        for (int k : data) t.insert(k);
    }
};

/* ------------------------------------------------------------------ */
TEST_F(TreapTest, HeapPropertyInitial)
{
    ASSERT_TRUE(t.isHeapOrdered()) << "Treap violates heap order on priorities";
}

/* ------------------------------------------------------------------ */
TEST_F(TreapTest, InorderSorted)
{
    auto inorder = t.inorder();
    auto expected = data;
    std::sort(expected.begin(), expected.end());
    ASSERT_EQ(expected, inorder);

    ASSERT_TRUE(t.isHeapOrdered());         // still a valid treap
}

/* ------------------------------------------------------------------ */
TEST_F(TreapTest, Search) {
    std::uniform_int_distribution<int> dist(0, 5100);
    for (int i = 0; i < 50; ++i) {
        int x = dist(rng);
        bool inData = (std::find(data.begin(), data.end(), x) != data.end());
        ASSERT_EQ(inData, t.contains(x))
            << "search(" << x << ") gave wrong result; "
            << "expected " << inData;
    }
}

/* ------------------------------------------------------------------ */
TEST_F(TreapTest, Delete)
{
    /* delete 50 random existing keys */
    std::shuffle(data.begin(), data.end(), rng);
    std::vector<int> toDelete(data.begin(), data.begin() + 50);

    for (int k : toDelete) {
        t.erase(k);
        data.erase(std::remove(data.begin(), data.end(), k), data.end());
    }
    std::sort(data.begin(), data.end());

    ASSERT_EQ(data, t.inorder());
    ASSERT_TRUE(t.isHeapOrdered());
}

/* ------------------------------------------------------------------ */
TEST_F(TreapTest, SplitMerge)
{
    /* (1) delete 20 random keys first */
    std::shuffle(data.begin(), data.end(), rng);
    std::vector<int> del20(data.begin(), data.begin() + 20);

    for (int k : del20) {
        t.erase(k);
        data.erase(std::remove(data.begin(), data.end(), k), data.end());
    }
    std::sort(data.begin(), data.end());

    /* (2) choose random pivot k */
    std::uniform_int_distribution<size_t> idxDist(0, data.size() - 1);
    int k = data[idxDist(rng)];

    auto [leftT, rightT] = t.split(k);          // t becomes empty

    auto leftKeys  = leftT.inorder();
    auto rightKeys = rightT.inorder();

    ASSERT_TRUE(std::all_of(leftKeys.begin(),  leftKeys.end(),
                            [k](int x){ return x <  k; }));
    ASSERT_TRUE(std::all_of(rightKeys.begin(), rightKeys.end(),
                            [k](int x){ return x >= k; }));

    /* (3) merge back and compare */
    Treap merged = Treap::merge(std::move(leftT), std::move(rightT));
    ASSERT_EQ(data, merged.inorder());
    ASSERT_TRUE(merged.isHeapOrdered());
}


