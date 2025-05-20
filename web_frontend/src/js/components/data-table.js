/**
 * 資料表格組件
 * 
 * 此組件負責處理資料表格的顯示與互動
 */

export function initDataTable() {
  Alpine.data('dataTable', () => ({
    columns: [],
    data: [],
    filteredData: [],
    sortColumn: '',
    sortDirection: 'asc',
    search: '',
    page: 1,
    pageSize: 10,
    loading: false,
    
    init() {
      this.$watch('search', () => {
        this.filterData();
        this.page = 1;
      });
    },
    
    async loadData(endpoint) {
      try {
        this.loading = true;
        const response = await window.apiService.getData(endpoint);
        this.columns = response.columns;
        this.data = response.data;
        this.filteredData = [...this.data];
      } catch (error) {
        console.error('載入資料失敗:', error);
      } finally {
        this.loading = false;
      }
    },
    
    filterData() {
      if (!this.search.trim()) {
        this.filteredData = [...this.data];
        return;
      }
      
      const searchTerm = this.search.toLowerCase();
      this.filteredData = this.data.filter(row => {
        return Object.values(row).some(value => 
          String(value).toLowerCase().includes(searchTerm)
        );
      });
    },
    
    toggleSort(column) {
      if (this.sortColumn === column) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortColumn = column;
        this.sortDirection = 'asc';
      }
      
      this.filteredData = [...this.filteredData].sort((a, b) => {
        let valueA = a[column];
        let valueB = b[column];
        
        // 處理字串和數字比較
        if (typeof valueA === 'string') {
          valueA = valueA.toLowerCase();
        }
        if (typeof valueB === 'string') {
          valueB = valueB.toLowerCase();
        }
        
        if (this.sortDirection === 'asc') {
          return valueA > valueB ? 1 : -1;
        } else {
          return valueA < valueB ? 1 : -1;
        }
      });
    },
    
    get paginatedData() {
      const start = (this.page - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredData.slice(start, end);
    },
    
    get totalPages() {
      return Math.ceil(this.filteredData.length / this.pageSize);
    }
  }));
}
