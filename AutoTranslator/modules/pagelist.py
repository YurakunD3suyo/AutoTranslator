import discord
from typing import Callable, Union, List

OPTIONS_PER_PAGE = 25


class PagedSelect(discord.ui.Select):
    def __init__(
        self,
        page: int,
        items: List[object],
        author_id: int,
        on_select: Callable[[discord.Interaction, object], None],
        label_getter: Callable[[object], str] = lambda item: str(item)
    ):
        self.page = page
        self.items = items
        self.author_id = author_id
        self.on_select_callback = on_select
        self.label_getter = label_getter

        total_pages = max(1, (len(items) + OPTIONS_PER_PAGE - 1) // OPTIONS_PER_PAGE)
        start = page * OPTIONS_PER_PAGE
        end = start + OPTIONS_PER_PAGE
        self.page_items = self.items[start:end]

        # itemインスタンス → SelectOption用 value に変換（idを文字列にして一意化）
        self.value_map = {str(id(item)): item for item in self.page_items}

        options = [
            discord.SelectOption(
                label=f"{i + 1}. {label_getter(item)}",
                value=str(id(item))
            )
            for i, item in enumerate(self.page_items, start=start)
        ]

        super().__init__(
            placeholder=f"ページ {page + 1} / {total_pages}",
            options=options,
            custom_id=f"paged_select_{author_id}"
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("この操作はコマンド実行者のみ可能です。", ephemeral=True)
            return

        selected_value = self.values[0]
        selected_item = self.value_map[selected_value]
        await self.on_select_callback(interaction, selected_item)


class PagedSelectView(discord.ui.View):
    def __init__(
        self,
        interact: discord.Interaction,
        options: List[Union[str, discord.SelectOption]],
        on_select: Callable[[discord.Interaction, str], None],
        label_getter: Callable[[object], str] = lambda item: str(item),
        timeout: int = 60,
        page: int = 0,
    ):
        super().__init__(timeout=timeout)
        self.interact = interact
        self.author_id = interact.user.id
        self.options = options
        self.on_select_callback = on_select
        self.label_getter = label_getter
        self.page = page

        # 初期の選択肢の更新を行う
        self.select = PagedSelect(self.page, self.options, self.author_id, self.on_select_callback, self.label_getter)
        self.add_item(self.select)

        self.prev_button = discord.ui.Button(emoji="⬅️", style=discord.ButtonStyle.secondary)
        self.next_button = discord.ui.Button(emoji="➡️", style=discord.ButtonStyle.secondary)

        self.prev_button.callback = self.go_prev
        self.next_button.callback = self.go_next

        self.add_item(self.prev_button)
        self.add_item(self.next_button)

        self.update_buttons()

    def update_select(self):
        """選択肢の再評価を行う"""
        self.remove_item(self.select)
        self.select = PagedSelect(self.page, self.options, self.author_id, self.on_select_callback, self.label_getter)
        self.add_item(self.select)

    def update_buttons(self):
        """ページボタンの状態更新"""
        self.prev_button.disabled = self.page <= 0
        self.next_button.disabled = (self.page + 1) * OPTIONS_PER_PAGE >= len(self.options)

    async def go_prev(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("この操作はコマンド実行者のみ可能です。", ephemeral=True)
            return

        if self.page > 0:
            self.page -= 1
            self.update_select()
            self.update_buttons()
            await interaction.response.edit_message(view=self)

    async def go_next(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("この操作はコマンド実行者のみ可能です。", ephemeral=True)
            return

        if (self.page + 1) * OPTIONS_PER_PAGE < len(self.options):
            self.page += 1
            self.update_select()
            self.update_buttons()
            await interaction.response.edit_message(view=self)
