-- Create database if not exists
-- Run: createdb card_game

-- Insert initial system questions
INSERT INTO questions (content, is_system, created_by) VALUES
-- Deep/Meaningful questions
('What''s something you wish more people knew about you?', true, NULL),
('What''s a fear you''ve never told anyone?', true, NULL),
('What''s the nicest thing someone has done for you?', true, NULL),
('What''s something you''re proud of but rarely talk about?', true, NULL),
('What do you wish you could tell your younger self?', true, NULL),
('What''s a dream you''ve given up on?', true, NULL),
('What''s something you need to forgive yourself for?', true, NULL),
('What''s the hardest thing you''ve ever had to do?', true, NULL),
('What makes you feel most alive?', true, NULL),
('What''s a belief you held strongly that you''ve changed your mind about?', true, NULL),
('What do you need more of in your life right now?', true, NULL),
('What''s something you''re currently struggling with?', true, NULL),
('If you could change one decision from your past, what would it be?', true, NULL),
('What''s the best advice you''ve ever received?', true, NULL),
('What does love mean to you?', true, NULL),

-- Fun/Casual questions
('What''s the most embarrassing song on your playlist?', true, NULL),
('If you could have any superpower for a day, what would it be?', true, NULL),
('What''s your guilty pleasure TV show?', true, NULL),
('What''s the weirdest food combination you enjoy?', true, NULL),
('If you won the lottery tomorrow, what''s the first thing you''d buy?', true, NULL),
('What''s your go-to karaoke song?', true, NULL),
('If you could live in any fictional world, which would it be?', true, NULL),
('What''s the most useless talent you have?', true, NULL),
('What''s your most unpopular opinion?', true, NULL),
('If you could only eat one food for the rest of your life, what would it be?', true, NULL),
('What''s the craziest thing on your bucket list?', true, NULL),
('If you were a superhero, what would your weakness be?', true, NULL),
('What''s the worst fashion choice you''ve ever made?', true, NULL),
('What''s your most irrational fear?', true, NULL),
('If you could instantly become an expert in something, what would it be?', true, NULL),

-- Connection questions
('What''s something you''ve always wanted to ask me?', true, NULL),
('What was your first impression of me?', true, NULL),
('What do you think we have in common?', true, NULL),
('What''s something you admire about the person to your left?', true, NULL),
('Describe me in three words.', true, NULL),
('What''s something you think I''m really good at?', true, NULL),
('What''s a memory you have of us that makes you smile?', true, NULL),
('What do you think is my biggest strength?', true, NULL),
('If we could go on any adventure together, what would it be?', true, NULL),
('What''s something you''ve learned from me?', true, NULL),
('What''s one thing you wish we did more together?', true, NULL),
('What do you value most about our friendship?', true, NULL),
('If you had to describe our relationship to a stranger, what would you say?', true, NULL),
('What''s something you think I should know about you?', true, NULL),
('What''s a compliment you''ve been meaning to give me?', true, NULL);
