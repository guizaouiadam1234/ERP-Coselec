import api from './api';

type MovementType = 'ENTRY' | 'EXIT';

export const StockService = {
  getCategories() {
    return api.get('/categories');
  },

  getProducts(categoryId?: number) {
    const url = categoryId ? `/products?category_id=${categoryId}` : '/products';
    return api.get(url);
  },

  getWarehouses() {
    return api.get('/warehouses');
  },

  getPartners() {
    return api.get('/partners');
  },

  getMovements() {
    return api.get('/stock-movements');
  },

  createMovement(payload: {
    product_id: number;
    warehouse_id: number;
    quantity: number;
    type: MovementType;
    partner_id: number | null;
    notes?: string;
  }) {
    const movementUrl = payload.type === 'ENTRY' ? '/stock/entry' : '/stock/exit';

    return api.post(movementUrl, {
      product_id: payload.product_id,
      warehouse_id: payload.warehouse_id,
      quantity: payload.quantity,
      partner_id: payload.partner_id
    });
  }
};