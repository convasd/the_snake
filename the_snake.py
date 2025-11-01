import time
from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет надписи на игровом поле - белый:
BOARD_TEXT_COLOR = (255, 255, 255)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка v1.03')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Основной класс игры"""

    def __init__(self) -> None:
        self.position = [(SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2)]
        self.body_color = None

    def draw(self) -> None:
        """метод класса прорисовки"""
        raise NotImplementedError(
            'Метод должен быть реализован в дочернем классе.')


class Apple(GameObject):
    """Дочерний класс Apple от GameObject"""

    def __init__(self) -> None:
        super().__init__()
        self.image = pygame.image.load('apple.png')

    def randomize_position(self, snake_position: list[list[int, int]],
                           snake_direction: list[list[int, int]]) -> None:
        """
        Метод классы получения случайных координат
        Поиск позиции появления Яблока будет происходить до тех пор,
        пока найденная позиция не будет удовлетворять требованию:
        позиция не попадает на тело Змейки, и
        не попадает на линию ее движения.
        """
        flag_in = True
        while flag_in:
            self.position = [
                (randint(0, (SCREEN_WIDTH - GRID_SIZE)) // GRID_SIZE)
                * GRID_SIZE,
                (randint(0, (SCREEN_HEIGHT - GRID_SIZE)) // GRID_SIZE)
                * GRID_SIZE]

            flag_in = not (
                (
                    self.position not in snake_position
                ) and not (
                    (
                        (self.position[0] == snake_position[0][0]
                         ) and (
                            snake_direction[0] == 0)
                    ) or (
                        (self.position[1] == snake_position[0][1]
                         ) and (
                             snake_direction[1] == 0))))

    def draw(self, surface: pygame.surface.Surface) -> None:
        """Метод класса прорисовки объекта Apple"""
        self.rect = self.image.get_rect(topleft=self.position)
        surface.blit(self.image, self.rect)


class Mine(GameObject):
    """Дочерний класс Mine от Apple"""

    def __init__(self) -> None:
        super().__init__()
        self.image = pygame.image.load('mine.png')
        self.position = []

    def randomize_position(self, snake_position: list[list[int, int]],
                           snake_direction: list,
                           apple_position: list) -> None:
        """
        Метод классы получения случайных координат для каждой мины
        Поиск позиции установки мины будет происзодить до тех пор,
        пока найденная позиция не будет удовлетворять требованию:
        позиция не попадает на тело Змейки и совпадать с позицией
        Яблока, и не попадает на линию движения Змейки.
        """
        for index in range(len(self.position)):
            flag_in = True
            while flag_in:
                self.position[index] = [
                    (randint(0, (SCREEN_WIDTH - GRID_SIZE)) // GRID_SIZE)
                    * GRID_SIZE,
                    (randint(0, (SCREEN_HEIGHT - GRID_SIZE)) // GRID_SIZE)
                    * GRID_SIZE]

                flag_in = not (
                    (
                        (
                            self.position[index] not in snake_position
                        ) and (
                            self.position[index] != apple_position)
                    ) and (
                        (
                            (
                                self.position[index][0] != snake_position[0][0]
                            ) and (
                                snake_direction[0] == 0)
                        ) or (
                            (
                                self.position[index][1] != snake_position[0][1]
                            ) and (
                                snake_direction[1] == 0))))

    def draw(self, surface: pygame.surface.Surface) -> None:
        """Метод класса прорисовки объекта Mine"""
        for position_index in self.position:
            self.rect = self.image.get_rect(topleft=tuple(position_index))
            surface.blit(self.image, self.rect)


class Snake(GameObject):
    """Наследуемый класс Snake от GameObject"""

    def __init__(self) -> None:
        super().__init__()
        self.positions = [[(SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2)]]
        self.last = [(SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2)]
        self.lenght = 1
        self.body_color = SNAKE_COLOR
        self.direction = RIGHT
        self.next_direction = None

    def draw(self) -> None:
        """Метод класса для прорисовки объекта Snake"""
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Затирание последнего сегмента
        if self.last:
            rect = (pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

    def update_direction(self) -> None:
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self) -> list:
        """Возвращает позицию головы Змейки"""
        return self.positions[0]

    def move(self) -> None:
        """Метод класса Snake, определяющий логику движения"""
        # Запоминаем последнюю ячейку, чтобы в дальнейшем ее скрыть.
        self.last = tuple(self.positions[len(self.positions) - 1])

        # Вперед двигается все тело (каждая клетка получает позицию
        # предыдущей по порядку от головы).
        for i in reversed(range(1, len(self.positions))):
            self.positions[i] = self.positions[i - 1].copy()

        # Получаем новую позицию головы.
        # Новое значение клетки - это смещение 20 точек
        # по направлению движения.
        result = [element * GRID_SIZE for element in self.direction]
        self.positions[0] = [x + y for x, y in zip(self.positions[0], result)]

        # Переносим голову в другую часть поля,
        # если голова должна уйти за его пределы.
        if self.positions[0][0] < 0:
            self.positions[0][0] = SCREEN_WIDTH - GRID_SIZE
        elif self.positions[0][0] > SCREEN_WIDTH - GRID_SIZE:
            self.positions[0][0] = 0

        if self.positions[0][1] < 0:
            self.positions[0][1] = SCREEN_HEIGHT - GRID_SIZE
        elif self.positions[0][1] > SCREEN_HEIGHT - GRID_SIZE:
            self.positions[0][1] = 0

    def reset(self) -> None:
        """Метод класса при проигрыше"""
        # Инициализировать шрифт и размер
        font = pygame.font.Font(None, 36)
        text = font.render('Вы проиграли!', True, BOARD_TEXT_COLOR)
        screen.blit(text, (250, 200))
        self.positions = [[(SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2)]]
        self.direction = [1, 0]
        pygame.display.update()
        time.sleep(2)


def handle_keys(game_object) -> None:
    """Функция обработки действий пользователя"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def level_visible(level: str) -> None:
    """Функция выводит уровень сложности."""
    font = pygame.font.Font(None, 20)
    text = font.render(level, True, BOARD_TEXT_COLOR)
    screen.blit(text, (0, 0))


def main() -> None:
    """Определяется вся логика игры."""
    pygame.init()
    apple = Apple()
    snake = Snake()
    mine = Mine()

    apple.randomize_position(snake.positions, snake.direction)

    while True:
        # Скорость перемещения Змейки зависит от ее длины.
        speed_corrector = len(snake.positions) // 5 + 1
        clock.tick(SPEED // 3 + speed_corrector)
        screen.fill((0, 0, 0))
        # На игровом поле показываем Уровень сложности игры.
        level_visible('Уровень сложности: ' + str(speed_corrector))

        # Начиная от 2 уровня на поле выставляем мину.
        if speed_corrector > 2:
            mine_visible = True
        else:
            mine_visible = False
            mine.position = []

        # Прорисовывыем объекты игры.
        apple.draw(screen)
        snake.draw()

        if mine_visible:
            mine.draw(screen)

        # Проверяем нажатие управляющих клавиш,
        # и если оно было, то изменяем направление движения Змейки.
        handle_keys(snake)
        snake.update_direction()

        # Если Змейка решила, "покушать себя" или попала на мину,
        # то "Игра закончилась"
        if (snake.get_head_position() in snake.positions[1:]) or (
                (snake.get_head_position() in mine.position) and mine_visible):
            snake.draw
            snake.reset()

        # Если Змейка съела яблоко, то она наращивает свои "мышцы",
        # а у мины и яблока новые координаты
        if snake.get_head_position() == apple.position:
            snake.positions.append(apple.position)
            apple.randomize_position(snake.positions, snake.direction)

            # Каждые 10 клеток Змейки увеличивается количество мин.
            if (len(snake.positions) % 10) == 0:
                mine.position.append([0, 0])
            if mine.position is not None:
                mine.randomize_position(snake.positions,
                                        snake.direction, apple.position)

        # Змейка просчитывает позиции клеток своего тела.
        snake.move()

        pygame.display.update()


if __name__ == '__main__':
    main()
