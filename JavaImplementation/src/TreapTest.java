import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import static org.junit.jupiter.api.Assertions.*;

/**
 *  Same functional tests as before, but we now keep the helper list
 *  `data` consistent with the actual Treap after every mutation
 *  (delete, split / merge).
 */
public class TreapTest {

    private final Random rnd = new Random();
    private Treap treap;
    private List<Integer> data;                 // ALWAYS mirrors treap’s keys

    /* ------------------------------------------------------------------ */
    @BeforeEach
    void setUp() {
        // 1 000 distinct integers in [0, 5000)
        data = IntStream.generate(() -> rnd.nextInt(5000))
                .distinct()
                .limit(1000)
                .boxed()
                .collect(Collectors.toCollection(ArrayList::new));

        treap = new Treap();
        data.forEach(treap::insert);
    }

    /* ------------------------------------------------------------------ */
    @Test
    void testInorderSorted() {
        List<Integer> expected = new ArrayList<>(data);
        Collections.sort(expected);                 // sort in place

        assertEquals(expected, treap.inorder(),
                "In‑order traversal is not sorted or lost keys");
    }

    /* ------------------------------------------------------------------ */
    @Test
    void testSearch() {
        IntStream.generate(() -> rnd.nextInt(5100)) // 50 random probes
                .limit(50)
                .forEach(x ->
                        assertEquals(data.contains(x), treap.search(x),
                                "search(" + x + ") produced wrong result"));
    }

    /* ------------------------------------------------------------------ */
    @Test
    void testDelete() {
        // Delete 50 random existing keys
        List<Integer> toDelete = rnd.ints(50, 0, data.size())
                .distinct()
                .mapToObj(data::get)
                .collect(Collectors.toList());

        toDelete.forEach(k -> {
            treap.delete(k);
            data.remove(Integer.valueOf(k));       // keep list in sync
        });

        List<Integer> expected = new ArrayList<>(data);
        Collections.sort(expected);

        assertEquals(expected, treap.inorder(),
                "inorder() after deletions does not match expectation");
    }

    /* ------------------------------------------------------------------ */
    @Test
    void testSplitMerge() {
        /* 1. Remove 20 random keys first */
        List<Integer> toDelete = rnd.ints(20, 0, data.size())
                .distinct()
                .mapToObj(data::get)
                .collect(Collectors.toList());

        toDelete.forEach(k -> {
            treap.delete(k);
            data.remove(Integer.valueOf(k));       // stay consistent
        });

        /* 2. Pick a random pivot k from the UPDATED data and split */
        Collections.sort(data);                    // ensure order
        int k = data.get(rnd.nextInt(data.size()));

        Treap[] parts = treap.split(k);
        Treap leftT  = parts[0];
        Treap rightT = parts[1];

        // sanity checks on split halves
        assertTrue(leftT.inorder().stream().allMatch(x -> x <  k),
                "Left split contains key ≥ pivot");
        assertTrue(rightT.inorder().stream().allMatch(x -> x >= k),
                "Right split contains key < pivot");

        /* 3. Merge halves back and verify against the **current** data */
        Treap merged = Treap.merge(leftT, rightT);

        assertEquals(data, merged.inorder(),
                "merge(left,right).inorder() differs from expected list");
    }
}
