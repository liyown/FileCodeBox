<template>
    <el-menu
      :default-active="activeIndex"
      class="el-menu-demo"
      mode="horizontal"
      @select="handleSelect"
    >
      <el-menu-item index="1">文件快递</el-menu-item>
      <el-menu-item index="2">云盘</el-menu-item>
      <el-menu-item index="3">云code</el-menu-item>
      <el-menu-item index="4">博客</el-menu-item>
      <el-menu-item index="5">后台</el-menu-item>
    </el-menu>
  </template>
  
<script lang="ts" setup>
  import { ref } from 'vue'
  import { ElMenu } from 'element-plus'
  import { useRouter } from 'vue-router';
import { ro } from 'element-plus/es/locale/index.mjs';

  const router = useRouter()
  const activeIndex = ref('1')
  const handleSelect = (key: string, keyPath: string[]) => {
    if (key === '1') {
        router.push('/')
    } else if (key === '2') {
        window.open('https://zfile.liuyaowen.club/')
    } else if (key === '3') {
        window.open('https://code.liuyaowen.club/')
    } else if (key === '4') {
        window.open('https://blog.liuyaowen.club/')
    } else if (key === '5') {
        window.open('https://1panel.liuyaowen.club/')
    }
  }
</script>
  