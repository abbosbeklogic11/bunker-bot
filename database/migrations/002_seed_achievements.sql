-- =============================================================
-- Migration 002: Seed achievements
-- =============================================================

INSERT INTO achievements (code, name, description, icon, reward_coins, reward_diamonds)
VALUES
  ('first_win',        'Birinchi Glaba',       'Birinchi marta oyin golib boldi',                    'trophy',  100, 2),
  ('five_wins',        'Besh Glaba',            'Besh marta oyin golib boldi',                        'star',    250, 5),
  ('ten_wins',         'O
 Glaba',             'O
 marta oyin golib boldi',                         'medal',   500, 10),
  ('twenty_five_wins', 'Yigirma besh Glaba',    'Yigirma besh marta oyin golib boldi',                'crown',   1000, 25),
  ('ten_protections',  'Qo
iqchi',               'O
 marta himoyadan foydalandi',                        'shield',  200, 3),
  ('strategist',       'Strateg',                 'Uch marta boshqasini eleminatsiya qilishda hal qiluvchi ovoz berdi', 'brain', 300, 5),
  ('diplomat',         'Diplomat',                'O
 marta ittifoq tuzdi',                               'handshake', 150, 2),
  ('detective',        'Detektiv',                'Boshqaning yashirin atributini topdi',                  'magnifier', 200, 3),
  ('survivor',         'Tirik qoluvchi',          'Oxirgi beshta oyinda eliminatsiyadan omon qoldi',      'heart',   250, 4),
  ('perfect_vote',     'Mukammal Ovoz',           'Har doim tog
i oyinchiga ovoz berdi',                'ballot',  300, 5),
  ('last_survivor',    'Oxirgi Tirik',            'Bunkerdagi so
ggi tirik qolgan oyinchi boldi',       'flag',    400, 7),
  ('mvp_first',        'Birinchi MVP',            'Birinchi marta MVP unvonini oldi',                      'lightning', 200, 3),
  ('speed_demon',      'Tez oyinchi',            'Ovoz berish bosqichida birinchi bolib ovoz berdi (5 marta)', 'rocket', 100, 1),
  ('social_butterfly', 'Ijtimoiy Kapalak',        'Bir oyinda barcha jonli oyinchilar bilan suhbatlashdi', 'butterfly', 150, 2)
ON CONFLICT (code) DO UPDATE
  SET name            = EXCLUDED.name,
      description     = EXCLUDED.description,
      icon            = EXCLUDED.icon,
      reward_coins    = EXCLUDED.reward_coins,
      reward_diamonds = EXCLUDED.reward_diamonds;
