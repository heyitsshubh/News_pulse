export interface ApiSuccess<T> {
  data: T;
}
export interface ApiErrorResponse {
  error: {
    message: string;
    statusCode: number;
  };
}
export interface PaginatedList<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}