"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import io
from typing import Literal, TYPE_CHECKING
from .errors import DiscordException
from .errors import InvalidArgument
from . import utils

__all__ = (
    'Asset',
)

if TYPE_CHECKING:
    ValidStaticFormatTypes = Literal['webp', 'jpeg', 'jpg', 'png']
    ValidAvatarFormatTypes = Literal['webp', 'jpeg', 'jpg', 'png', 'gif']

VALID_STATIC_FORMATS = frozenset({"jpeg", "jpg", "webp", "png"})
VALID_AVATAR_FORMATS = VALID_STATIC_FORMATS | {"gif"}

class Asset:
    """Represents a CDN asset on Discord.

    .. container:: operations

        .. describe:: str(x)

            Returns the URL of the CDN asset.

        .. describe:: len(x)

            Returns the length of the CDN asset's URL.

        .. describe:: bool(x)

            Checks if the Asset has a URL.

        .. describe:: x == y

            Checks if the asset is equal to another asset.

        .. describe:: x != y

            Checks if the asset is not equal to another asset.

        .. describe:: hash(x)

            Returns the hash of the asset.
    """
    __slots__ = ('_state', '_url')

    BASE = 'https://cdn.discordapp.com'

    def __init__(self, state, url=None):
        self._state = state
        self._url = url

    @classmethod
    def _from_avatar(cls, state, user, *, format=None, static_format='webp', size=1024):
        if not utils.valid_icon_size(size):
            raise InvalidArgument("size must be a power of 2 between 16 and 4096")
        if format is not None and format not in VALID_AVATAR_FORMATS:
            raise InvalidArgument(f"format must be None or one of {VALID_AVATAR_FORMATS}")
        if format == "gif" and not user.is_avatar_animated():
            raise InvalidArgument("non animated avatars do not support gif format")
        if static_format not in VALID_STATIC_FORMATS:
            raise InvalidArgument(f"static_format must be one of {VALID_STATIC_FORMATS}")

        if user.avatar is None:
            return user.default_avatar_url

        if format is None:
            format = 'gif' if user.is_avatar_animated() else static_format

        return cls(state, f'/avatars/{user.id}/{user.avatar}.{format}?size={size}')

    @classmethod
    def _from_icon(cls, state, object, path, *, format='webp', size=1024):
        if object.icon is None:
            return cls(state)

        if not utils.valid_icon_size(size):
            raise InvalidArgument("size must be a power of 2 between 16 and 4096")
        if format not in VALID_STATIC_FORMATS:
            raise InvalidArgument(f"format must be None or one of {VALID_STATIC_FORMATS}")

        url = f'/{path}-icons/{object.id}/{object.icon}.{format}?size={size}'
        return cls(state, url)

    @classmethod
    def _from_cover_image(cls, state, obj, *, format='webp', size=1024):
        if obj.cover_image is None:
            return cls(state)

        if not utils.valid_icon_size(size):
            raise InvalidArgument("size must be a power of 2 between 16 and 4096")
        if format not in VALID_STATIC_FORMATS:
            raise InvalidArgument(f"format must be None or one of {VALID_STATIC_FORMATS}")

        url = f'/app-assets/{obj.id}/store/{obj.cover_image}.{format}?size={size}'
        return cls(state, url)

    @classmethod
    def _from_guild_image(cls, state, id, hash, key, *, format='webp', size=1024):
        if not utils.valid_icon_size(size):
            raise InvalidArgument("size must be a power of 2 between 16 and 4096")
        if format not in VALID_STATIC_FORMATS:
            raise InvalidArgument(f"format must be one of {VALID_STATIC_FORMATS}")

        if hash is None:
            return cls(state)

        return cls(state, f'/{key}/{id}/{hash}.{format}?size={size}')

    @classmethod
    def _from_guild_icon(cls, state, guild, *, format=None, static_format='webp', size=1024):
        if not utils.valid_icon_size(size):
            raise InvalidArgument("size must be a power of 2 between 16 and 4096")
        if format is not None and format not in VALID_AVATAR_FORMATS:
            raise InvalidArgument(f"format must be one of {VALID_AVATAR_FORMATS}")
        if format == "gif" and not guild.is_icon_animated():
            raise InvalidArgument("non animated guild icons do not support gif format")
        if static_format not in VALID_STATIC_FORMATS:
            raise InvalidArgument(f"static_format must be one of {VALID_STATIC_FORMATS}")

        if guild.icon is None:
            return cls(state)

        if format is None:
            format = 'gif' if guild.is_icon_animated() else static_format

        return cls(state, f'/icons/{guild.id}/{guild.icon}.{format}?size={size}')

    @classmethod
    def _from_sticker_url(cls, state, sticker, *, size=1024):
        if not utils.valid_icon_size(size):
            raise InvalidArgument("size must be a power of 2 between 16 and 4096")

        return cls(state, f'/stickers/{sticker.id}/{sticker.image}.png?size={size}')

    @classmethod
    def _from_emoji(cls, state, emoji, *, format=None, static_format='png'):
        if format is not None and format not in VALID_AVATAR_FORMATS:
            raise InvalidArgument(f"format must be None or one of {VALID_AVATAR_FORMATS}")
        if format == "gif" and not emoji.animated:
            raise InvalidArgument("non animated emoji's do not support gif format")
        if static_format not in VALID_STATIC_FORMATS:
            raise InvalidArgument(f"static_format must be one of {VALID_STATIC_FORMATS}")
        if format is None:
            format = 'gif' if emoji.animated else static_format

        return cls(state, f'/emojis/{emoji.id}.{format}')

    def __str__(self):
        return self.BASE + self._url if self._url is not None else ''

    def __len__(self):
        if self._url:
            return len(self.BASE + self._url)
        return 0

    def __bool__(self):
        return self._url is not None

    def __repr__(self):
        return f'<Asset url={self._url!r}>'

    def __eq__(self, other):
        return isinstance(other, Asset) and self._url == other._url

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._url)

    async def read(self):
        """|coro|

        Retrieves the content of this asset as a :class:`bytes` object.

        .. warning::

            :class:`PartialEmoji` won't have a connection state if user created,
            and a URL won't be present if a custom image isn't associated with
            the asset, e.g. a guild with no custom icon.

        .. versionadded:: 1.1

        Raises
        ------
        DiscordException
            There was no valid URL or internal connection state.
        HTTPException
            Downloading the asset failed.
        NotFound
            The asset was deleted.

        Returns
        -------
        :class:`bytes`
            The content of the asset.
        """
        if not self._url:
            raise DiscordException('Invalid asset (no URL provided)')

        if self._state is None:
            raise DiscordException('Invalid state (no ConnectionState provided)')

        return await self._state.http.get_from_cdn(self.BASE + self._url)

    async def save(self, fp, *, seek_begin=True):
        """|coro|

        Saves this asset into a file-like object.

        Parameters
        ----------
        fp: Union[BinaryIO, :class:`os.PathLike`]
            Same as in :meth:`Attachment.save`.
        seek_begin: :class:`bool`
            Same as in :meth:`Attachment.save`.

        Raises
        ------
        DiscordException
            There was no valid URL or internal connection state.
        HTTPException
            Downloading the asset failed.
        NotFound
            The asset was deleted.

        Returns
        --------
        :class:`int`
            The number of bytes written.
        """

        data = await self.read()
        if isinstance(fp, io.IOBase) and fp.writable():
            written = fp.write(data)
            if seek_begin:
                fp.seek(0)
            return written
        else:
            with open(fp, 'wb') as f:
                return f.write(data)
