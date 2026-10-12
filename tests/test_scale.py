import unittest
from app import app
from models import Recipe

class TestRecipeScalingAndOrdering(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_recipes_list_endpoint(self):
        resp = self.client.get('/api/recipes?volume=5.0')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertGreaterEqual(len(data), 10)
        for r in data:
            self.assertEqual(r['target_volume_gal'], 5.0)
            self.assertGreater(len(r['malts']), 0)

    def test_single_recipe_volume_scaling(self):
        recipe = Recipe.query.first()
        r5 = self.client.get(f'/api/recipes/{recipe.id}?volume=5.0').get_json()
        r10 = self.client.get(f'/api/recipes/{recipe.id}?volume=10.0').get_json()
        self.assertAlmostEqual(
            r10['malts'][0]['amount_lb'],
            r5['malts'][0]['amount_lb'] * 2.0,
            places=1
        )

    def test_multi_recipe_ordering_list(self):
        recipes = Recipe.query.limit(3).all()
        ids = [r.id for r in recipes]
        resp = self.client.post('/api/ordering-list', json={
            'recipe_ids': ids,
            'volume_gal': 5.0
        })
        self.assertEqual(resp.status_code, 200)
        order = resp.get_json()
        self.assertEqual(order['summary']['selected_recipe_count'], 3)
        self.assertEqual(order['summary']['total_batch_volume_gal'], 15.0)
        self.assertGreater(len(order['ordering_list']['malts']), 0)
        self.assertGreater(len(order['ordering_list']['hops']), 0)

if __name__ == '__main__':
    unittest.main()
