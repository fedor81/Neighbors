// Типы зеркалят backend Pydantic-схемы (app/schemas/schemas.py).
export type BookingStatus = "pending"|"approved"|"rejected"|"rented"|"returned"|"disputed"|"cancelled";
export type ItemStatus = "available"|"booked"|"rented"|"hidden";
export type CatalogMode = "local"|"city";

export interface Item { id:number; title:string; description?:string; category:{id:number;slug:string;name:string}; deposit_amount:string; status:ItemStatus; owner:{id:number;name?:string;rating?:number;reviews_count:number}; main_photo_url?:string; distance_m?:number }
export interface Booking { id:number; item_id:number; renter_id:number; status:BookingStatus; deposit_held_amount:string; start_date?:string; end_date?:string; created_at:string }
export interface Wallet { total:string; held:string; available:string }
