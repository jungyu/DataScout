## Sliding Window（滑動視窗）入門指引

### 1. 定位與應用 (Positioning and Applications)

*   **定位：** 滑動視窗是一種常用的演算法技巧，特別適用於處理陣列（Array）、字串（String）或連結串列（LinkedList）等資料結構中**連續（Contiguous）**子序列（Subarray/Substring）相關的問題。它通常用於優化暴力法解決方案的時間複雜度。
*   **應用：** 滑動視窗模式廣泛應用於尋找：
    *   固定大小連續子陣列的最大/最小總和或平均值 (如您範例所示)。
    *   滿足特定條件的最長或最短連續子陣列。
    *   字串匹配問題 (如尋找包含特定字元的最小子字串、變位詞/字母異位詞)。
    *   計算固定窗口內的統計數據 (如最大值、頻率等)。

*   **為何使用？** 相較於暴力法（Brute-force），暴力法通常會遍歷所有可能的子序列並計算，如果子序列大小為 K，總長度為 N，暴力法的時間複雜度可能高達 O(N*K)。而滑動視窗通過巧妙地移動「窗口」，在每一步只對新進入和離開窗口的元素進行處理，**避免了對窗口內重疊部分的重複計算**，從而將時間複雜度降低到 O(N)。

### 2. 模型原理 (Core Principle and Model)

滑動視窗的核心思想是維護一個在資料序列上移動的「窗口」。這個窗口可以有固定的大小，也可以根據問題的條件調整大小。其基本流程如下：

1.  **初始化窗口：** 設置一個窗口的起始位置（Start Pointer，例如 `start`）和結束位置（End Pointer，例如 `end`），通常初始時 `start = 0`，`end` 也從 0 或 K-1 開始。同時初始化一個變數（例如 `current_sum`, `max_length`, `char_frequency_map`）來記錄當前窗口的相關資訊或結果。
2.  **擴展窗口：** 使用一個迴圈（通常是 `for` 迴圈或 `while` 迴圈），讓結束指標 `end` 向右移動，逐一將新元素納入窗口。
3.  **更新窗口內數據：** 每當 `end` 指標右移一個位置，將新的元素加入當前的相關計算中（例如，將新元素的值加到 `current_sum` 中，或者更新字符頻率表）。
4.  **檢查並處理窗口：** 在迴圈的某個階段，根據問題需求檢查當前窗口是否滿足特定條件（例如，窗口大小是否達到 K，或者窗口內的總和是否超過某個值）。
    *   如果窗口滿足條件，則進行必要的處理（例如，計算平均值並存入結果列表，或者更新找到的最佳子序列的長度/總和）。
    *   **對於固定大小的窗口 (如範例)，** 當窗口大小達到 K 時 (`end - start + 1 == K`，或對於從 `end=0` 開始的迴圈，當 `end >= K-1` 時)，我們就處理這個窗口。
    *   **對於可變大小的窗口，** 條件檢查會根據問題不同而變化。
5.  **縮小窗口：** 在處理完窗口後（尤其對於固定大小的窗口，或者可變窗口需要縮小時），將起始指標 `start` 向右移動，從窗口中移除最左邊的元素，並更新相關的計算值（例如，從 `current_sum` 中減去 `arr[start]` 的值）。這是實現 O(N) 效率的關鍵步驟，避免了重新計算整個窗口的總和。
6.  **重複步驟 2-5：** 持續移動 `end` 指標，直到遍歷完整個資料序列。

### 3. 如何收集、整理資料 (Data Collection and Organization)

*   **資料收集：** 對於滑動視窗演算法本身來說，它通常假設輸入數據已經被組織成一個序列（如陣列 `arr`）。在實際應用中，這些數據可能來自：
    *   檔案讀取。
    *   資料庫查詢。
    *   API 請求。
    *   使用者輸入。
    *   感測器數據流 (例如時間序列數據)。
    *   網路封包。
    *   對於初學者理解演算法，通常會直接給定一個陣列作為輸入。

*   **資料整理：** 滑動視窗演算法的處理對象是**連續**的序列。因此，資料通常需要被整理成一個有序的列表或陣列。任何需要處理的屬性（例如，您範例中的數字值，或者如果是股票數據，可能是每日收盤價、成交量等）會被組織到這個序列中。
    *   **在演算法內部，** 數據的整理體現為：
        *   **總和 (Sum):** 像您範例中計算平均值，需要維護窗口內元素的總和。每次窗口移動，從總和中減去最左邊的元素，加上最右邊的新元素。
        *   **計數/頻率 (Count/Frequency Map):** 對於字串問題或需要統計元素出現次數的問題，會使用哈希表 (Hash Map/Dictionary) 來記錄窗口內各元素的計數。窗口移動時，更新對應元素的計數。
        *   **最大/最小值 (Max/Min):** 可能需要使用雙端佇列 (Deque) 或其他數據結構來高效地跟蹤窗口內的最大或最小值。

### 4. 如何解讀報告 (Interpreting Results)

「報告」在這裡可以理解為演算法的輸出結果。如何解讀取決於具體問題的目標：

*   **計算所有固定窗口的平均值 (如範例所示)：** 輸出是一個列表，列表中的每一個元素對應著原始陣列中一個 K 大小的連續子陣列的平均值。您範例中的 `[2.2, 2.8, 2.4, 3.6, 2.8]` 就表示第一個 5 元素的窗口平均是 2.2，第二個 5 元素的窗口平均是 2.8，以此類推。
*   **尋找最長/最短子序列：** 輸出通常是一個數字（最長/最短長度）或子陣列/子字串本身，或其起始/結束索引。解讀時，這個數字代表滿足條件的子序列的最大/最小長度，而子序列則直接展示了該結果。
*   **尋找滿足特定條件的子序列：** 輸出可能是一個布林值（是否存在）、滿足條件的第一個子序列、所有滿足條件的子序列列表等。解讀時根據輸出的形式來判斷問題的答案。

**總結來說，** 滑動視窗是一個強大的優化工具，用於處理序列數據上的連續子結構問題。它的核心在於通過窗口的移動和增量式地更新窗口內數據，將時間複雜度從 O(N*K) 降低到 O(N)。理解其「擴展-處理-縮小」的模式以及如何維護窗口內的狀態是掌握這種技巧的關鍵。