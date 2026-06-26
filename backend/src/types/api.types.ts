// Generic success wrapper
export interface ApiSuccess<T> {
  data: T;
}

// Generic error shape
export interface ApiErrorResponse {
  error: {
    message: string;
    statusCode: number;
  };
}

// Paginated list helper (reserved for future use)
export interface PaginatedList<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}
