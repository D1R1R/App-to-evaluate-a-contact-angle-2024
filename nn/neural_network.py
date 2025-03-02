import os
import torch
from torch import nn, optim
import torchvision.transforms as tr
from PIL import Image

from dependensies.parametrs import PATH_TO_WEIGHTS, IMG_SIZE
from ui_settings.child_window_ui import ChildWindow_BAR


device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')  # TODO: Ask user about device
# -------------------------UNET-------------------------
class Downsample_block(nn.Module):
  def __init__(self, in_channels: int, out_channels: int, padding: int=1) -> None:
    super().__init__()
    self.conv_block_in = nn.Sequential(
         nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=3, padding=padding),
         nn.ReLU(),
    )
    self.conv_block = nn.Sequential(
         nn.Conv2d(in_channels=out_channels, out_channels=out_channels, kernel_size=3, padding=padding),
         nn.ReLU(),
    )
    self.pool = nn.MaxPool2d((2, 2))

  def forward(self, x):
    x = self.conv_block_in(x)
    x = self.conv_block(x)
    x_pooled = self.pool(x)
    return x, x_pooled


class Upsample_block(nn.Module):
  def __init__(self, in_channels: int, out_channels: int, padding: int=1) -> None:
    super().__init__()
    self.conv_block_in = nn.Sequential(
         nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=3, padding=padding),
         nn.ReLU(),
    )
    self.conv_block = nn.Sequential(
         nn.Conv2d(in_channels=out_channels, out_channels=out_channels, kernel_size=3, padding=padding),
         nn.ReLU(),
    )
    self.unpool = nn.ConvTranspose2d(in_channels=in_channels, out_channels=out_channels, kernel_size=2, stride=2)  # stride=2??

  def forward(self, x: torch.Tensor, skip: torch.Tensor) -> torch.Tensor:
    x = self.unpool(x)
    x = torch.cat((x, skip), axis=1)  # skip connection
    x = self.conv_block_in(x)
    x = self.conv_block(x)

    return x


class UNet(nn.Module):
  def __init__(self, padding: int = 1) -> None:
    super().__init__()
    self.db1 = Downsample_block(in_channels=3, out_channels=64)
    self.db2 = Downsample_block(in_channels=64, out_channels=128)
    self.db3 = Downsample_block(in_channels=128, out_channels=256)
    self.db4 = Downsample_block(in_channels=256, out_channels=512)

    self.bottom = nn.Sequential(
        nn.Conv2d(in_channels=512, out_channels=1024, kernel_size=3, padding=padding),
        nn.ReLU(),
        nn.Conv2d(in_channels=1024, out_channels=1024, kernel_size=3, padding=padding),
        nn.LeakyReLU(),
    )

    self.ub1 = Upsample_block(in_channels=1024, out_channels=512)
    self.ub2 = Upsample_block(in_channels=512, out_channels=256)
    self.ub3 = Upsample_block(in_channels=256, out_channels=128)
    self.ub4 = Upsample_block(in_channels=128, out_channels=64)

    self.out = nn.Conv2d(in_channels=64, out_channels=1, kernel_size=1, padding=0)

  def forward(self, x: torch.Tensor) -> torch.Tensor:
    x1, x = self.db1(x)
    x2, x = self.db2(x)
    x3, x = self.db3(x)
    x4, x = self.db4(x)

    x = self.bottom(x)

    x = self.ub1(x, x4)
    x = self.ub2(x, x3)
    x = self.ub3(x, x2)
    x = self.ub4(x, x1)

    out = self.out(x)

    return out

  def process(self, x: torch.Tensor) -> torch.Tensor:
        return self(x)
# -------------------------Utility-------------------------
def load_chekpoint(model: nn.Module, file_name: str, optim: optim.Optimizer=None) -> None:
  state = torch.load(os.path.join(PATH_TO_WEIGHTS, file_name), map_location=torch.device(device))
  model.load_state_dict(state["model"])
  if optim:
    optim.load_state_dict(state["optimizer"])
  model.eval()

def initialize_nn() -> nn.Module:
  model = UNet().to(device)
  # Загружаем веса
  load_chekpoint(model, "UNET_FULL_params_ep30.pt")
  return model

def predict(model: nn.Module, path_x: torch.Tensor, state: bool) -> torch.Tensor:
  bar = ChildWindow_BAR()
  bar.show()
  
  in_image_tr = tr.Compose([
    tr.Resize(IMG_SIZE),
    tr.Grayscale(num_output_channels=3),
    tr.ToTensor(),
  ])
  sizes_list = list()
  x = list()
  if not state:
    # Folder
    for imgs in os.listdir(path_x):
      img = os.path.join(path_x, imgs)
      img = Image.open(img)
      sizes_list.append(img.size[::-1])
      img = in_image_tr(img)
      x.append(img)
  else:
    # Single file
    img = Image.open(path_x)
    sizes_list.append(img.size[::-1])
    img = in_image_tr(img)
    x.append(img)
  x = torch.stack(x)  
  # prediction = model.process(x)
  prediction = list()
  for img_idx in range(x.shape[0]):
    single_img = x[img_idx].unsqueeze(0)
    predictoin_x = model.process(single_img)
    prediction.append(predictoin_x)
    bar.progress_bar.setValue(img_idx)
  prediction = torch.cat(prediction, dim=0)
  prediction[prediction < 0] = 0
  prediction[prediction > 0] = 1
  prediction = [tr.ToPILImage()(pred_mask) for pred_mask in prediction]
  for idx in range(len(sizes_list)):
    size = sizes_list[idx]
    prediction[idx] = tr.Resize(size)(prediction[idx])
  return prediction